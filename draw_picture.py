from typing import Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import ui
import models as md
import datetime
import DATA

def set_weight_plot_limits(ax, historical_weights, predicted_weights=None):
    """统一设置体重图表的Y轴范围"""
    all_weights = list(historical_weights)

    if predicted_weights is not None:
        all_weights.extend(predicted_weights)

    if st.session_state.target_weight is not None:
        all_weights.append(st.session_state.target_weight)

    if len(all_weights) > 0:
        min_weight = min(all_weights)
        max_weight = max(all_weights)
        padding = (max_weight - min_weight) * 0.1
        ax.set_ylim(min_weight - padding, max_weight + padding)
    else:
        ax.set_ylim(30, 120)  # 默认范围

def plot_weight_trend(df: pd.DataFrame, days: int = 90):
    """增强的体重趋势图表"""
    if 'df' in locals() and df.empty:
        ui.create_info_box("暂无数据", "info")
        return

    end_date = df['date'].max()
    start_date = end_date - pd.Timedelta(days=days)
    sub = df[(df['date'] >= start_date) & (df['date'] <= end_date)].sort_values('date')

    if len(sub) < 2:
        ui.create_info_box(f"最近 {days} 天数据不足，无法绘制趋势图。", "warning")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # 使用渐变色填充
    ax.plot(sub['date'], sub['weight'], marker='o', linewidth=3,
            markersize=6, color='#4cc9f0', label='历史体重', alpha=0.8)

    # 添加目标线
    if st.session_state.target_weight is not None:
        target_weight = st.session_state.target_weight
        ax.axhline(y=target_weight, color='#ff6b6b', linestyle='--',
                   alpha=0.8, linewidth=2, label=f'目标体重: {target_weight}kg')

    # 图表美化
    ax.set_title(f'📈 最近{days}天体重变化趋势', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('体重 (kg)', fontsize=12)

    # 动态调整Y轴范围
    set_weight_plot_limits(ax, sub['weight'])

    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(loc='best', fontsize=10)

    # 美化背景
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')

    fig.autofmt_xdate(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

def plot_calorie_balance(df: pd.DataFrame, days: int = 30):
    if 'df' in locals() and df.empty:
        st.info("暂无数据")
        return

    end_date = df['date'].max()
    start_date = end_date - pd.Timedelta(days=days)
    sub = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()

    if len(sub) < 2:
        st.info(f"最近 {days} 天数据不足，无法绘制图表。")
        return

    sub['calorie_burn'] = sub.apply(lambda r: DATA.EXERCISE_Kkcal.get(r['exercise_type'], 0) *
                                              (r['weight'] if not pd.isna(r['weight']) else 0) *
                                              (0 if pd.isna(r['exercise_time']) else r['exercise_time']) / 60 +
                                              DATA.BMR_COEFFICIENT * (r['weight'] if not pd.isna(r['weight']) else 0) * 24,
                                    axis=1)

    # 🔹 calorie_intake 统一估算
    sub['calorie_intake'] = sub.apply(
        lambda r: r['weight'] * 30 if pd.isna(r['calorie_intake']) else r['calorie_intake'],
        axis=1
    )

    sub = sub.sort_values('date')
    x = np.arange(len(sub))

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(x, sub['calorie_intake'], alpha=0.7, label='摄入热量')
    ax.bar(x, sub['calorie_burn'], alpha=0.7, label='消耗热量')
    ax.set_title(f'最近{days}天热量收支平衡')
    ax.set_xlabel('日期')
    ax.set_ylabel('热量 (大卡)')
    ax.set_xticks(x)
    ax.set_xticklabels(sub['date'].dt.strftime('%m-%d'), rotation=35)
    ax.grid(True, axis='y', linestyle='--', alpha=0.6)
    ax.legend()
    st.pyplot(fig)

def plot_history_with_prediction(df: pd.DataFrame, pred: Dict):

    if pred.get('status') != 'success':
        st.info("预测结果无效。")
        return

    # 准备历史数据
    hist = df.copy().sort_values('date')
    if len(hist) > 90:
        hist = hist.tail(90)

    # 提取预测数据
    pred_dates = [p['date'] for p in pred['predictions']]
    pred_weights = [p['weight'] for p in pred['predictions']]

    # 计算不确定性（基于历史波动性）
    hist_std = hist['weight'].std() if len(hist) > 1 else 0.5
    pred_stds = [hist_std * (1 + i * 0.1) for i in range(len(pred_dates))]  # 随时间增加不确定性

    fig, ax = plt.subplots(figsize=(14, 8))

    # 1. 历史数据
    ax.plot(hist['date'], hist['weight'], marker='o', linewidth=2.5,
            markersize=6, color='#2E86AB', label='历史体重', alpha=0.8)

    # 2. 预测数据（均值）
    ax.plot(pred_dates, pred_weights, marker='s', linestyle='-', linewidth=2.5,
            markersize=5, color='#A23B72', label='LSTM预测体重', alpha=0.9)

    # 3. 不确定性区间（95%置信区间）
    upper_bound = [weight + 1.96 * std for weight, std in zip(pred_weights, pred_stds)]
    lower_bound = [weight - 1.96 * std for weight, std in zip(pred_weights, pred_stds)]

    ax.fill_between(pred_dates, lower_bound, upper_bound, alpha=0.2,
                    color='#F18F01', label='95%置信区间')

    # 4. 目标体重线
    if st.session_state.target_weight is not None:
        target_weight = st.session_state.target_weight
        ax.axhline(y=target_weight, color='#C73E1D', linestyle='--', linewidth=2,
                   alpha=0.8, label=f'目标体重: {target_weight}kg')

        # 添加健康减重速率参考线
        current_weight = hist['weight'].iloc[-1] if not hist.empty else pred_weights[0]
        days = len(pred_dates)

        # 健康减重速率：每周0.5-1kg
        healthy_rate_fast = 1.0 / 7  # 每周1kg
        healthy_rate_slow = 0.5 / 7  # 每周0.5kg

        fast_target = current_weight - healthy_rate_fast * days
        slow_target = current_weight - healthy_rate_slow * days

        # 确保不超过目标体重
        fast_target = max(target_weight, fast_target)
        slow_target = max(target_weight, slow_target)

        ax.axhline(y=fast_target, color='#F0B67F', linestyle=':', alpha=0.6,
                   label='积极减重参考线(1kg/周)')
        ax.axhline(y=slow_target, color='#84BC9C', linestyle=':', alpha=0.6,
                   label='稳健减重参考线(0.5kg/周)')

    # 5. 当前时间分隔线
    last_hist_date = hist['date'].iloc[-1] if not hist.empty else pred_dates[0]
    ax.axvline(x=last_hist_date, color='#6D6875', linestyle='--', alpha=0.7,
               linewidth=1.5, label='预测起始点')

    # 6. 图表样式美化
    ax.set_title(f"LSTM智能体重预测 ({len(pred_dates)}天)\n带不确定性估计和健康参考",
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12, fontweight='bold')
    ax.set_ylabel('体重 (kg)', fontsize=12, fontweight='bold')

    # 动态调整Y轴范围
    all_weights = list(hist['weight']) + pred_weights + upper_bound + lower_bound
    if st.session_state.target_weight is not None:
        all_weights.append(st.session_state.target_weight)

    if all_weights:
        min_weight = min(all_weights)
        max_weight = max(all_weights)
        padding = (max_weight - min_weight) * 0.15
        ax.set_ylim(min_weight - padding, max_weight + padding)

    # 网格和图例
    ax.grid(True, linestyle='--', alpha=0.3, which='both')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)

    # 日期格式优化
    fig.autofmt_xdate(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

    # 7. 添加统计信息
    if len(pred_weights) > 1:
        total_change = pred_weights[-1] - pred_weights[0]
        avg_daily_change = total_change / (len(pred_weights) - 1)
        weekly_change = avg_daily_change * 7

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("预计总变化", f"{total_change:+.1f}kg")
        with col2:
            st.metric("日均变化", f"{avg_daily_change:+.2f}kg/天")
        with col3:
            color = "normal" if abs(weekly_change) <= 1.0 else "inverse"
            st.metric("周均变化", f"{weekly_change:+.2f}kg/周",
                      delta_color=color)

        # 健康提示
        if abs(weekly_change) > 1.0:
            st.warning("⚠️ 预测减重速率超出健康范围（推荐每周0.5-1kg）")
        elif 0.5 <= abs(weekly_change) <= 1.0:
            st.success("✅ 预测减重速率在健康范围内")
        else:
            st.info("ℹ️ 预测减重速率较慢，可能需要调整计划")

def display_prediction_results(df, training_plan=None):
    days = st.session_state.get('prediction_days', 28)

    # 首先检查数据量是否足够
    if len(df) < 10:
        st.warning(f"数据量不足，需要至少10条记录才能进行预测。当前已有{len(df)}条记录，请继续录入数据。")
        return

    model, scalers = md.load_lstm()

    # 检查模型是否存在
    if model is None:
        # 尝试训练模型
        with st.spinner("正在训练预测模型..."):
            train_result = md.train_lstm(df)
            # 检查训练结果
            if train_result.get("status") == "error":
                st.error(f"模型训练失败: {train_result.get('message')}")
                return

            # 重新加载模型
            model, scalers = md.load_lstm()
            if model is None:
                st.error("模型训练后仍无法加载。")
                st.info("这可能是因为数据量不足或数据格式问题。请继续记录更多数据。")
                return

    # 执行预测
    with st.spinner("正在计算体重预测..."):
        pred = model.predict_future_lstm(df, model, scalers, days, training_plan=training_plan)

    if pred['status'] != 'success':
        st.error(pred['message'])
        return

    # 显示预测结果
    c1, c2, c3 = st.columns(3)
    c1.metric("起始体重", pred['start_weight'])
    c2.metric("预测结束体重", pred['end_weight'])
    c3.metric("预计变化", pred['weight_change'])

    plot_history_with_prediction(df, pred)

    st.markdown("**预测结果预览**")
    preview = pd.DataFrame(pred['predictions'])
    if len(preview) > 10:
        preview = pd.concat([preview.head(5), preview.tail(5)], ignore_index=True)
    st.dataframe(preview, use_container_width=True)

def create_weight_input_form():
    """创建美观的体重输入表单"""
    with st.form("weight_form", clear_on_submit=True):
        ui.create_section_header("📝 添加体重记录", "")

        col_date, col_weight = st.columns(2)
        with col_date:
            date = st.date_input("日期", value=datetime.date.today(),
                                 key="weight_date")
        with col_weight:
            weight = st.number_input("体重(kg)", min_value=0.0, max_value=200.0,
                                     value=70.0, step=0.1, key="weight_input")

        submitted = st.form_submit_button("💾 保存记录",
                                          use_container_width=True,
                                          type="primary")

        if submitted:
            return date, weight
    return None, None