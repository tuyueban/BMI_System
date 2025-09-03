import pickle
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import os
import streamlit as st
import bmi_calculation
import numpy as np
import Plan
import DATA

def load_data(path: str = None) -> pd.DataFrame:
    """加载健康数据"""
    # 在函数内部获取路径
    if path is None:
        # 检查session_state是否已初始化
        if hasattr(st, 'session_state') and hasattr(st.session_state, 'current_user'):
            path = DATA.get_data_file(st.session_state.current_user)
        else:
            path = DATA.get_data_file()  # 使用默认路径

    if os.path.exists(path):
        df = pd.read_csv(path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce', format='mixed')
            df = df.dropna(subset=['date'])
        return df
    else:
        return pd.DataFrame(columns=['date', 'weight', 'height', 'exercise_type', 'exercise_time', 'calorie_intake'])

def save_data(df: pd.DataFrame, path: str = None) -> None:
    """保存健康数据"""
    if path is None:
        # 检查session_state是否已初始化
        if hasattr(st, 'session_state') and hasattr(st.session_state, 'current_user'):
            path = DATA.get_data_file(st.session_state.current_user)
        else:
            path = DATA.get_data_file()  # 使用默认路径
    df.to_csv(path, index=False)

def build_base_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """基础的数据处理框架"""
    data = df.copy().sort_values('date')
    data['days_since_start'] = (data['date'] - data['date'].min()).dt.days

    # 确保所有必要列都存在并有合理值
    default_values = {
        'exercise_type': '无',
        'exercise_time': 30,
        'calorie_intake': data['weight'] * 30 if 'weight' in data.columns else 0,
        'height': st.session_state.user_height if hasattr(st, 'session_state') and hasattr(st.session_state, 'user_height') else 170.0
    }

    for col, default_val in default_values.items():
        if col not in data.columns:
            data[col] = default_val
        else:
            data[col] = data[col].fillna(default_val)

    # 计算BMI
    data['bmi'] = data.apply(
        lambda r: bmi_calculation.calculate_bmi(r['weight'], r['height']),
        axis=1
    )

    # 使用科学BMR计算基础代谢 - 移到函数内部检查
    user_age = st.session_state.user_age if hasattr(st, 'session_state') and hasattr(st.session_state, 'user_age') else 30
    user_sex = st.session_state.user_sex if hasattr(st, 'session_state') and hasattr(st.session_state, 'user_sex') else "男"

    data['basal_metabolism'] = data.apply(
        lambda r: bmi_calculation.calculate_bmr(r['weight'], r['height'], user_age, user_sex),
        axis=1
    )

    # 计算运动消耗
    data['exercise_burn'] = data.apply(
        lambda r: DATA.EXERCISE_Kkcal.get(r['exercise_type'], 0) * r['exercise_time'],
        axis=1
    )

    # 计算总消耗
    data['calorie_burn'] = data['basal_metabolism'] + data['exercise_burn']

    # 计算热量缺口
    data['calorie_gap'] = data['calorie_intake'] - data['calorie_burn']

    # 添加日期相关特征
    data['day_of_week'] = data['date'].dt.dayofweek
    data['day_of_month'] = data['date'].dt.day
    data['month'] = data['date'].dt.month

    return data

def ensure_schema(df: pd.DataFrame) -> pd.DataFrame:
    for col, dtype in {
        'date': 'datetime64[ns]',
        'weight': 'float',
        'height': 'float',
        'exercise_type': 'object',
        'exercise_time': 'float',
        'calorie_intake': 'float'
    }.items():
        if col not in df.columns:
            df[col] = pd.Series(dtype=dtype)

    if not np.issubdtype(df['date'].dtype, np.datetime64):
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df = df.dropna(subset=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # 使用设置的身高来补充缺失的身高数据
    if 'height' in df.columns and df['height'].isna().any():
        # 检查session_state是否已初始化
        if hasattr(st, 'session_state') and hasattr(st.session_state, 'user_height'):
            df['height'] = df['height'].fillna(st.session_state.user_height)
        else:
            df['height'] = df['height'].fillna(170.0)  # 默认值

    # 统一补齐 calorie_intake
    df['calorie_intake'] = df.apply(
        lambda r: r['weight'] * 30 if pd.isna(r['calorie_intake']) else r['calorie_intake'],
        axis=1
    )
    return df

def check_abnormal(df: pd.DataFrame):
    if len(df) < 2:
        return
    changes = df['weight'].diff().abs()
    abnormal_days = df[changes > 3]
    if not abnormal_days.empty:
        st.error(f"⚠️ 检测到体重波动异常（超过3kg）: {abnormal_days['date'].dt.strftime('%Y-%m-%d').tolist()}")

def build_training_frame(df: pd.DataFrame, training_plan=None, diet_plan=None) -> pd.DataFrame:
    """增强版的数据处理框架，包含锻炼计划和饮食计划的影响"""
    data = build_base_training_frame(df)

    # 添加日期相关特征
    if 'day_of_week' not in data.columns:
        data['day_of_week'] = data['date'].dt.dayofweek

    # 初始化计划列
    data['planned_exercise'] = 0
    data['planned_calorie_intake'] = 0

    # 如果有锻炼计划，计算计划执行情况
    if training_plan is not None and not training_plan.empty:
        data['planned_exercise'] = data.apply(
            lambda r: Plan.get_planned_exercise(r['date'], training_plan), axis=1
        )

    # 如果有饮食计划，计算计划热量
    if diet_plan is not None and not diet_plan.empty:
        data['planned_calorie_intake'] = data.apply(
            lambda r: Plan.get_planned_calories(r['date'], diet_plan), axis=1
        )

    return data

def build_training_sequences(df: pd.DataFrame, training_plan=None, diet_plan=None, seq_len: int = 7):
    """构建训练序列，目标为 Δweight"""
    data = build_training_frame(df, training_plan, diet_plan)

    if len(data) < seq_len + 1:
        st.warning(f"数据不足: 需要至少{seq_len + 1}条记录，当前只有{len(data)}条")
        return None, None, None

    # 特征列
    feature_columns = ['day_of_week', 'planned_exercise', 'planned_calorie_intake']

    # 确保所有特征列都存在
    for col in feature_columns:
        if col not in data.columns:
            data[col] = 0

    # 构建特征
    features = data[feature_columns].fillna(0).values

    # 构建目标（Δweight）
    target = data['weight'].diff().fillna(0).values.reshape(-1, 1)

    # 标准化
    scaler_x = MinMaxScaler(feature_range=(0, 1))
    scaler_y = MinMaxScaler(feature_range=(0, 1))

    features_scaled = scaler_x.fit_transform(features)
    target_scaled = scaler_y.fit_transform(target)

    x, y = [], []
    for i in range(seq_len, len(features_scaled)):
        x.append(features_scaled[i - seq_len:i])
        y.append(target_scaled[i])

    if len(x) == 0:
        st.error("无法构建训练序列：序列长度太短")
        return None, None, None

    return np.array(x), np.array(y), (scaler_x, scaler_y)

def train_lstm(df, user_training_plan, diet_plan):
    """
    训练 LSTM 模型，并返回特征数量
    """
    # 构建训练数据
    training_data = build_training_frame(df, user_training_plan, diet_plan)

    if len(training_data) < 8:  # 至少需要序列长度+1条记录
        return {"status": "error", "message": f"数据不足，需要至少8条记录，当前只有{len(training_data)}条"}

    # 构建训练序列
    x, y, scalers = build_training_sequences(df, user_training_plan, diet_plan, seq_len=7)

    if x is None or y is None:
        return {"status": "error", "message": "无法构建训练序列"}

    n_features = x.shape[2]  # 获取特征数量

    # 创建并编译模型
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(x.shape[1], x.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    # 添加回调函数
    callbacks = [
        EarlyStopping(monitor='loss', patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor='loss', factor=0.5, patience=5, min_lr=0.0001)
    ]

    # 训练模型
    model.fit(x, y, epochs=100, batch_size=32, verbose=0, callbacks=callbacks)

    # 保存模型和Scaler
    model_path = DATA.get_model_file(st.session_state.current_user)
    scaler_path = DATA.get_scaler_file(st.session_state.current_user)

    model.save(model_path)
    with open(scaler_path, "wb") as f:
        pickle.dump(scalers, f)  # 保存 scaler

    return {"status": "success", "n_features": n_features}


def load_lstm():
    try:
        # 检查模型文件和Scaler文件是否存在
        model_path = DATA.get_model_file(st.session_state.current_user)
        scaler_path = DATA.get_scaler_file(st.session_state.current_user)

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            # 确保文件不为空
            if os.path.getsize(model_path) > 0 and os.path.getsize(scaler_path) > 0:
                # 清除任何现有的Keras会话，避免冲突
                import tensorflow as tf
                tf.keras.backend.clear_session()

                # 加载模型
                model = load_model(model_path, compile=False)
                model.compile(optimizer="adam", loss="mse")

                # 加载scaler
                with open(scaler_path, "rb") as f:
                    scalers = pickle.load(f)
                return model, scalers

        # 如果模型或Scaler不可用，返回None
        return None, None
    except Exception as e:
        st.error(f"模型加载错误: {str(e)}")
        # 删除损坏的文件以便重新训练
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(scaler_path):
            os.remove(scaler_path)
        return None, None

def apply_reasonable_constraints(pred_weight, current_weight, historical_weights):
    # 健康减重范围：每周0.5-1kg
    max_weekly_loss = 1.0  # kg/周
    max_daily_change = max_weekly_loss / 7  # 约0.14kg/天

    # 约束每日变化
    if pred_weight < current_weight - max_daily_change:
        constrained_weight = current_weight - max_daily_change
    elif pred_weight > current_weight + max_daily_change:
        constrained_weight = current_weight + max_daily_change
    else:
        constrained_weight = pred_weight

    # 添加合理波动（±0.3kg）
    import random
    daily_fluctuation = random.uniform(-0.3, 0.3)
    constrained_weight += daily_fluctuation

    return round(constrained_weight, 1)


def predict_future_lstm(df: pd.DataFrame, model=None, scalers=None, days: int = 28,
                        training_plan=None, diet_plan=None, seq_len: int = 7):
    """预测未来体重（基于 Δweight 累加）"""

    # 尝试加载模型
    if model is None or scalers is None:
        model, scalers = load_lstm()

    if model is None or scalers is None:
        st.warning("模型未找到，正在重新训练模型...")
        # 自动训练新的模型
        train_result = train_lstm(df, training_plan, diet_plan)
        if train_result.get("status") == "error":
            st.error(f"模型训练失败: {train_result.get('message')}")
            return {"status": "error", "message": "无法进行预测，请稍后再试。"}

        # 重新加载模型
        model, scalers = load_lstm()
        if model is None:
            st.error("模型训练后仍无法加载")
            return {"status": "error", "message": "无法加载新模型"}

    # 进行体重预测
    data = build_training_frame(df, training_plan, diet_plan)
    if data.empty:
        return {"status": "error", "message": "没有数据，无法预测。"}
    if len(data) < seq_len:
        return {"status": "error", "message": f"数据不足，至少需要 {seq_len} 条记录进行预测。"}

    scaler_x, scaler_y = scalers
    last_weight = float(data.iloc[-1]['weight'])
    last_height = data.iloc[-1]['height']
    last_date = data['date'].max()

    features = data[['day_of_week', 'planned_exercise', 'planned_calorie_intake']].fillna(0).values
    features_scaled = scaler_x.transform(features)
    last_seq = features_scaled[-seq_len:].copy()

    preds = []
    current_weight = last_weight
    user_age = st.session_state.user_age
    user_sex = st.session_state.user_sex

    # 清除任何现有的Keras会话，避免名称作用域冲突
    import tensorflow as tf
    tf.keras.backend.clear_session()

    for i in range(days):
        pred_date = last_date + pd.Timedelta(days=i + 1)
        day_of_week = pred_date.dayofweek
        planned_exercise = Plan.get_planned_exercise(pred_date, training_plan) if training_plan is not None else 0
        planned_calories = Plan.get_planned_calories(pred_date, diet_plan) if diet_plan is not None else 0

        # 确保序列形状正确
        if last_seq.shape[0] != seq_len:
            st.error(f"序列长度不正确: 期望 {seq_len}, 实际 {last_seq.shape[0]}")
            return {"status": "error", "message": "序列长度错误"}

        # 预测 Δweight
        try:
            delta_scaled = model.predict(last_seq.reshape(1, seq_len, -1), verbose=0)
            delta_weight = float(scaler_y.inverse_transform(delta_scaled)[0][0])
        except Exception as e:
            st.error(f"预测错误: {str(e)}")
            return {"status": "error", "message": f"预测失败: {str(e)}"}

        # 更新体重
        pred_weight = current_weight + delta_weight
        pred_weight = apply_reasonable_constraints(pred_weight, current_weight, data['weight'].values)

        pred_bmi = bmi_calculation.calculate_bmi(pred_weight, last_height)
        basal_metabolism = bmi_calculation.calculate_bmr(pred_weight, last_height, user_age, user_sex)
        total_calorie_burn = basal_metabolism + planned_exercise
        planned_gap = planned_calories - total_calorie_burn

        # 更新序列（新的一天特征）
        new_features = np.array([[day_of_week, planned_exercise, planned_calories]])
        new_features_scaled = scaler_x.transform(new_features)
        last_seq = np.vstack([last_seq[1:], new_features_scaled])

        preds.append({
            "date": pred_date,
            "weight": round(pred_weight, 2),
            "bmi": round(pred_bmi, 2),
            "planned_exercise": round(planned_exercise, 1),
            "planned_calories": round(planned_calories, 1),
            "total_calorie_burn": round(total_calorie_burn, 1),
            "basal_metabolism": round(basal_metabolism, 1)
        })

        current_weight = pred_weight

    # 平滑一下曲线
    preds_df = pd.DataFrame(preds)
    preds_df['weight'] = preds_df['weight'].rolling(window=3, min_periods=1, center=True).mean()
    preds = preds_df.to_dict(orient="records")

    return {
        "status": "success",
        "predictions": preds,
        "start_date": preds[0]['date'] if preds else None,
        "end_date": preds[-1]['date'] if preds else None,
        "start_weight": round(last_weight, 1),
        "end_weight": preds[-1]['weight'] if preds else None,
        "weight_change": round(preds[-1]['weight'] - last_weight, 1) if preds else None,
    }