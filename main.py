import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests
import ui
import models
import Plan
import bmi_calculation
import recommendation
import draw_picture
import DATA
from models import train_lstm

def display_health_overview(df):
    """改进的健康概览显示"""
    if 'df' in locals() and df.empty:
        ui.create_info_box("尚无数据，请在'添加记录'页录入或导入数据。", "info")
        return

    # 使用设置的身高计算BMI
    df['height'] = df['height'].fillna(st.session_state.user_height)
    df['bmi'] = df.apply(lambda r: bmi_calculation.calculate_bmi(r['weight'], r['height']), axis=1)
    latest = df.sort_values('date').iloc[-1]
    bmi_val = float(latest['bmi'])
    cat, advice = bmi_calculation.get_bmi_category(bmi_val)

    # 使用卡片布局显示指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ui.create_metric_card("最新日期", latest['date'].strftime('%Y-%m-%d'))
    with col2:
        ui.create_metric_card("体重(kg)", f"{latest['weight']}")
    with col3:
        ui.create_metric_card("BMI", f"{bmi_val}")
    with col4:
        ui.create_metric_card("体重状态", cat)

    # 显示建议
    ui.create_info_box(advice, "info")




# 解决中文显示
try:
    plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial Unicode MS"]
except Exception:
    pass
plt.rcParams["axes.unicode_minus"] = False

# =========================
# Streamlit 页面
# =========================
import user_manager
from user_manager import user_manager

# 在设置页面配置后添加登录检查
st.set_page_config(page_title="BMI体质评估与预测系统", layout="wide")
ui.inject_custom_css()

# 用户登录检查
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if st.session_state.current_user is None:
    # 显示登录/注册界面
    st.markdown("## 👋 欢迎使用BMI体质评估与预测系统")

    tab1, tab2 = st.tabs(["登录", "注册"])

    with tab1:
        username = st.text_input("用户名", key="login_username")
        if st.button("登录", key="login_btn"):
            if username.strip():
                if user_manager.user_exists(username):
                    user_manager.login(username)
                    st.success(f"欢迎回来，{username}！")
                    st.rerun()
                else:
                    st.error("用户不存在，请先注册")
            else:
                st.warning("请输入用户名")

    with tab2:
        new_username = st.text_input("新用户名", key="register_username")
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("身高(cm)", min_value=50.0, max_value=250.0, value=170.0)
        with col2:
            age = st.number_input("年龄", min_value=10, max_value=100, value=30)

        sex = st.radio("性别", ["男", "女"])
        activity_level = st.selectbox("活动水平", ["久坐", "轻度活动", "中度活动", "高强度活动", "非常活跃"])

        if st.button("注册", key="register_btn"):
            if new_username.strip():
                if not user_manager.user_exists(new_username):
                    user_config = {
                        'user_height': height,
                        'user_age': age,
                        'user_sex': sex,
                        'user_activity_level': activity_level
                    }
                    user_manager.create_user(new_username, user_config)
                    user_manager.login(new_username)
                    st.success(f"注册成功！欢迎，{new_username}！")
                    st.rerun()
                else:
                    st.error("用户名已存在")
            else:
                st.warning("请输入用户名")

    st.stop()

st.set_page_config(page_title="BMI体质评估与预测系统", layout="wide")
ui.inject_custom_css()

st.markdown(f"## 🧍‍♀️ BMI 体质评估与预测系统 - 用户: {st.session_state.current_user}")
st.caption("记录体重、饮食与运动，帮你科学预测健康趋势 ✨")

tabs = st.tabs(["📊 概览", "➕ 添加记录", "📈 趋势分析", "🔮 体重预测", "⚙️ 个人设置"])


# 初始化会话状态
if 'df' not in st.session_state:
    st.session_state.df = models.ensure_schema(models.load_data(DATA.DATA_FILE))
if 'training_plan' not in st.session_state:
    st.session_state.training_plan = None
if 'prediction_days' not in st.session_state:
    st.session_state.prediction_days = 28
if 'show_prediction' not in st.session_state:
    st.session_state.show_prediction = False
if 'num_exercises' not in st.session_state:
    st.session_state.num_exercises = 1
if 'target_weight' not in st.session_state:
    st.session_state.target_weight = None
if 'user_height' not in st.session_state:
    st.session_state.user_height = 170.0
if 'user_sex' not in st.session_state:
    st.session_state.user_sex = "男"
if 'user_age' not in st.session_state:
    st.session_state.user_age = 30
if 'user_activity_level' not in st.session_state:
    st.session_state.user_activity_level = "轻度活动"
if 'user_training_plan' not in st.session_state:
    st.session_state.user_training_plan = None
if 'target_baseline_weight' not in st.session_state:
    st.session_state.target_baseline_weight = None
if 'target_set_date' not in st.session_state:
    st.session_state.target_set_date = None
if 'food_log' not in st.session_state:
    st.session_state.food_log = pd.DataFrame(columns=[
        'date', 'food_name', 'brand', 'quantity', 'unit',
        'calories', 'protein', 'carbs', 'fat', 'fiber', 'sodium'
    ])
if 'diet_goals' not in st.session_state:
    st.session_state.diet_goals = {
        'calories': 2000,
        'protein': 70,
        'carbs': 250
    }
if 'today_food_entries' not in st.session_state:
    st.session_state.today_food_entries = []
# 删除重复的df初始化代码
# if 'df' not in st.session_state:
#    st.session_state.df = pd.DataFrame(columns=[
#        'date', 'weight', 'height', 'exercise_type',
#        'exercise_time', 'calorie_intake'
#    ])
if "found_food" not in st.session_state:
    st.session_state.found_food = []
if 'diet_plan' not in st.session_state:
    st.session_state.diet_plan = pd.DataFrame(columns=[
        'meal', 'name', 'brand', 'quantity', 'unit',
        'calories', 'protein', 'carbs', 'fat', 'days_per_week'
    ])


# ============ 概览 =============
with tabs[0]:
    ui.create_page_header("健康概览", "查看您的健康数据和进度概览", "📊")
    overview_df = st.session_state.df.copy()
    models.check_abnormal(overview_df)
    if st.button("📄 生成30天健康报告"):
        last30 = overview_df.tail(30)
        recommendation.export_report(last30)
    if overview_df.empty:
        st.info("尚无数据，请在'添加记录'页录入或导入数据。")
    else:
        # 使用设置的身高计算BMI
        overview_df['height'] = overview_df['height'].fillna(st.session_state.user_height)
        overview_df['bmi'] = overview_df.apply(lambda r: bmi_calculation.calculate_bmi(r['weight'], r['height']), axis=1)
        latest = overview_df.sort_values('date').iloc[-1]
        bmi_val = float(latest['bmi'])
        cat, advice = bmi_calculation.get_bmi_category(bmi_val)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("最新日期", latest['date'].strftime('%Y-%m-%d'))
        c2.metric("体重(kg)", f"{latest['weight']}")
        c3.metric("BMI", f"{bmi_val}")
        c4.metric("体重状态", cat)
        st.info(advice)

        # 目标管理区域
        st.markdown("---")
        st.subheader("🎯 目标管理")

        col_target1, col_target2 = st.columns([2, 1])

        with col_target1:
            # 显示当前目标或设置新目标
            if st.session_state.target_weight is not None:
                st.info(f"当前目标体重: **{st.session_state.target_weight} kg**")
            else:
                st.warning("尚未设置目标体重")

        # 目标进度分析（仅在设置了目标时显示）
        current_weight = float(latest['weight'])
        target_weight = st.session_state.target_weight

        # 基线体重：优先用设定目标时记录的基线；如果还没保存过目标，就用最早一条记录兜底
        baseline_w = st.session_state.target_baseline_weight
        if baseline_w is None and not overview_df.empty:
            baseline_w = float(overview_df.sort_values('date').iloc[0]['weight'])

        if target_weight is not None:
            weight_diff = current_weight - target_weight  # >0 代表需要减重；<0 代表需要增重


            def clip01(x):  # 保障 0~1
                return max(0.0, min(1.0, x))


            if baseline_w is not None:
                if weight_diff > 0:
                    # 减重：总目标量 = 基线 - 目标；已完成 = 基线 - 当前
                    total = baseline_w - target_weight
                    done = baseline_w - current_weight
                    progress = 1.0 if total <= 0 else clip01(done / total)
                    st.progress(progress,
                                text=f"减重进度：{progress * 100:.1f}%（已减 {max(0.0, done):.1f}/{max(0.0, total):.1f} kg）")
                elif weight_diff < 0:
                    # 增重：总目标量 = 目标 - 基线；已完成 = 当前 - 基线
                    total = target_weight - baseline_w
                    done = current_weight - baseline_w
                    progress = 1.0 if total <= 0 else clip01(done / total)
                    st.progress(progress,
                                text=f"增重进度：{progress * 100:.1f}%（已增 {max(0.0, done):.1f}/{max(0.0, total):.1f} kg）")
                else:
                    st.progress(1.0, text="目标达成：100%")
            else:
                st.info("尚未有基线体重，请在'个人设置'中设置目标体重")

            # 详细数据区域
            st.markdown("---")
            st.subheader("📊 详细数据")

            # 计算热量消耗（修复计算）
            if len(overview_df) > 0:
                # 计算最近7天的平均数据
                recent_data = overview_df.tail(7).copy()  # 使用copy避免修改原数据

                # 设置运动数据的默认值
                default_exercise_type = '无'
                default_exercise_time = 0  # 默认无运动

                # 填充缺失的运动数据
                if 'exercise_type' not in recent_data.columns or recent_data['exercise_type'].isna().all():
                    recent_data['exercise_type'] = default_exercise_type
                else:
                    recent_data['exercise_type'] = recent_data['exercise_type'].fillna(default_exercise_type)

                if 'exercise_time' not in recent_data.columns or recent_data['exercise_time'].isna().all():
                    recent_data['exercise_time'] = default_exercise_time
                else:
                    recent_data['exercise_time'] = recent_data['exercise_time'].fillna(default_exercise_time)

                # 正确计算热量消耗（使用默认值）
                recent_data['calorie_burn'] = recent_data.apply(
                    lambda r: (DATA.EXERCISE_Kkcal.get(r['exercise_type'], 0) * r['exercise_time']) +
                              (DATA.BMR_COEFFICIENT * r['weight'] * 24),
                    axis=1
                )

                # 计算摄入热量的默认值（体重*30）
                if 'calorie_intake' not in recent_data.columns or recent_data['calorie_intake'].isna().all():
                    recent_data['calorie_intake'] = recent_data['weight'] * 30
                else:
                    recent_data['calorie_intake'] = recent_data['calorie_intake'].fillna(recent_data['weight'] * 30)

                # 计算平均值
                avg_weight = recent_data['weight'].mean()
                avg_intake = recent_data['calorie_intake'].mean()
                avg_burn = recent_data['calorie_burn'].mean()
                avg_exercise_time = recent_data['exercise_time'].mean()

                col_data1, col_data2, col_data3, col_data4 = st.columns(4)

                st.metric("平均摄入", f"{avg_intake:.0f} kcal")
                st.metric("平均消耗", f"{avg_burn:.0f} kcal")
                balance = avg_intake - avg_burn
                st.metric("热量平衡", f"{balance:+.0f} kcal")

# ============ 添加记录 =============
with tabs[1]:
    st.subheader("📝 添加体重记录")
    col_date, col_weight = st.columns(2)
    with col_date:
        date = st.date_input("日期", value=datetime.date.today(), key="weight_date")
    with col_weight:
        weight = st.number_input("体重(kg)", min_value=0.0, max_value=200.0, value=70.0, step=0.1,
                                 key="weight_input")
    # 在每个tab的末尾添加自动保存
    for tab in tabs:
        # 在tab内容结束后添加
        user_manager.save_user_data()
    # ================= 食物记录 =================
    st.subheader("🍽️ 今日饮食记录")

    # 输入食物名称
    food_query = st.text_input("输入食物名称")

    # 搜索按钮
    if st.button("🔍 搜索") and food_query:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_query}&search_simple=1&action=process&json=1&page_size=100"
        try:
            response = requests.get(url)
            data = response.json()

            if data.get("products"):
                st.session_state.found_food = []
                for product in data["products"]:
                    nutriments = product.get("nutriments", {})

                    # 获取热量（优先 kcal，若没有则用 kJ 转换）
                    calories = nutriments.get("energy-kcal_100g")
                    if calories is None:
                        energy_kj = nutriments.get("energy_100g")
                        if energy_kj is not None:
                            calories = round(energy_kj / 4.184, 2)
                        else:
                            calories = 0

                    st.session_state.found_food.append({
                        "name": product.get("product_name", "未知"),
                        "brand": product.get("brands", "未知"),
                        "calories": calories,
                        "protein": nutriments.get("proteins_100g", 0),
                        "carbs": nutriments.get("carbohydrates_100g", 0),
                        "fat": nutriments.get("fat_100g", 0)
                    })

                st.success(f"共找到 {len(st.session_state.found_food)} 个相关结果")
            else:
                st.warning("未找到相关食物，请尝试输入更具体的名称。")

        except Exception as e:
            st.error(f"查询食物时出错: {e}")

    # 显示找到的食物并让用户选择
    if "found_food" in st.session_state and st.session_state.found_food:
        st.markdown("---")

        # 创建选择框让用户选择食物
        food_options = [
            f"{food['brand']} - {food['name']} ({food['calories']} kcal/100g)"
            for food in st.session_state.found_food
        ]

        selected_food_index = st.selectbox(
            "选择要添加的食物",
            range(len(food_options)),
            format_func=lambda i: food_options[i]
        )

        selected_food = st.session_state.found_food[selected_food_index]

        # 自定义摄入量输入
        col_qty1, col_qty2 = st.columns(2)
        with col_qty1:
            quantity = st.number_input(
                "摄入量 (g)",
                min_value=1,
                max_value=2000,
                value=100,
                step=10,
                key="food_quantity"
            )
        with col_qty2:
            # 显示估算的热量
            estimated_calories = selected_food['calories'] * (quantity / 100)
            st.metric("估算热量", f"{estimated_calories:.0f} kcal")

        # 只有一个添加按钮
        if st.button("➕ 添加到今日饮食记录", key="add_to_today_food"):
            # 计算实际营养值
            factor = quantity / 100
            food_entry = {
                'name': selected_food['name'],
                'brand': selected_food['brand'],
                'quantity': quantity,
                'unit': 'g',
                'calories': selected_food['calories'] * factor,
                'protein': selected_food['protein'] * factor,
                'carbs': selected_food['carbs'] * factor,
                'fat': selected_food['fat'] * factor
            }

            # 添加到今日饮食记录
            if "today_food_entries" not in st.session_state:
                st.session_state.today_food_entries = []
            st.session_state.today_food_entries.append(food_entry)
            st.success(f"已添加: {selected_food['name']} {quantity}g")

    # 显示今日饮食记录表格
    if "today_food_entries" in st.session_state and st.session_state.today_food_entries:
        st.markdown("---")
        st.subheader("📊 今日饮食记录详情")

        # 创建显示用的DataFrame
        display_df = pd.DataFrame(st.session_state.today_food_entries)

        # 重新排列列的顺序
        display_df = display_df[['name', 'brand', 'quantity', 'unit', 'calories', 'protein', 'carbs', 'fat']]

        # 重命名列名
        display_df.columns = ['食物名称', '品牌', '数量', '单位', '热量(kcal)', '蛋白质(g)', '碳水(g)', '脂肪(g)']

        # 显示表格
        st.dataframe(display_df, use_container_width=True)

        # 计算总计
        total_calories = display_df['热量(kcal)'].sum()
        total_protein = display_df['蛋白质(g)'].sum()
        total_carbs = display_df['碳水(g)'].sum()
        total_fat = display_df['脂肪(g)'].sum()

        # 显示总计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总热量", f"{total_calories:.0f} kcal")
        with col2:
            st.metric("总蛋白质", f"{total_protein:.1f} g")
        with col3:
            st.metric("总碳水", f"{total_carbs:.1f} g")
        with col4:
            st.metric("总脂肪", f"{total_fat:.1f} g")

        # 清空按钮
        if st.button("🗑️ 清空今日饮食记录", key="clear_today_food"):
            st.session_state.today_food_entries = []
            st.rerun()
    else:
        total_calories = weight * 30

    # 主表单（体重和运动记录）
    st.subheader("🏋️ 运动记录")

    # 获取用户设置的身高
    user_height = st.session_state.user_height or 170.0

    # 根据锻炼计划自动计算今日运动
    today_exercise = None

    # 手动运动记录
    st.markdown("**今日实际运动**")

    # 初始化运动记录列表
    if "exercise_entries" not in st.session_state:
        st.session_state.exercise_entries = [{'type': today_exercise[0] if today_exercise else '无',
                                              'time': today_exercise[1] if today_exercise else 0.0}]

    exercises = []
    for i in range(len(st.session_state.exercise_entries)):
        cols = st.columns(2)
        with cols[0]:
            # 使用session_state中保存的值
            exercise_type = st.selectbox("运动类型", list(DATA.EXERCISE_Kkcal.keys()),
                                         index=list(DATA.EXERCISE_Kkcal.keys()).index(
                                             st.session_state.exercise_entries[i]['type']),
                                         key=f"exercise_type_{i}")
        with cols[1]:
            exercise_time = st.number_input("时长(分钟)", min_value=0.0, max_value=600.0,
                                            value=st.session_state.exercise_entries[i]['time'],
                                            step=5.0, key=f"exercise_time_{i}")
        exercises.append((exercise_type, exercise_time))

        # 更新session_state中的值
        st.session_state.exercise_entries[i] = {'type': exercise_type, 'time': exercise_time}

    # 添加更多运动按钮
    if st.button("➕ 添加更多运动", key="add_more_exercise"):
        # 添加一个新的空运动记录
        st.session_state.exercise_entries.append({'type': '无', 'time': 0.0})
        st.rerun()

    # 计算总运动时长和主要运动类型
    total_duration = sum(dur for (typ, dur) in exercises)
    main_type = exercises[0][0] if exercises else '无'

    # 计算总摄入热量
    calorie_intake = total_calories if st.session_state.today_food_entries else weight * 30

    # 提交按钮
    if st.button("✅ 提交所有记录", key="submit_all_records", use_container_width=True):
        # 创建健康数据记录
        new_row = pd.DataFrame([{
            'date': pd.to_datetime(date),
            'weight': float(weight),
            'height': float(user_height),
            'exercise_type': main_type,
            'exercise_time': float(total_duration),
            'calorie_intake': float(calorie_intake)
        }])

        # 更新健康数据
        new_df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        new_df = new_df.sort_values('date').drop_duplicates('date', keep='last')
        st.session_state.df = models.ensure_schema(new_df)

        # 保存饮食记录到专门的饮食日志
        for food in st.session_state.today_food_entries:
            food_log_entry = {
                'date': pd.to_datetime(date),
                'food_name': food['name'],
                'brand': food['brand'],
                'quantity': food['quantity'],
                'unit': 'g',
                'calories': food['calories'],
                'protein': food['protein'],
                'carbs': food['carbs'],
                'fat': food['fat'],
                'fiber': 0,
                'sodium': 0
            }
            st.session_state.food_log = pd.concat([
                st.session_state.food_log,
                pd.DataFrame([food_log_entry])
            ], ignore_index=True)
        user_manager.save_user_data()
        st.success("所有记录已成功提交！")
        # 提交后清空运动记录
        st.session_state.exercise_entries = [{'type': '无', 'time': 0.0}]
        st.session_state.today_food_entries = []
        st.session_state.show_prediction = True
        st.rerun()
    # 数据导入模块
    st.markdown("---")
    st.subheader("📂 批量数据导入")
    col_import, col_export = st.columns(2)

    with col_import:
        uploaded_file = st.file_uploader("上传健康数据CSV文件", type="csv")
        if uploaded_file is not None:
            try:
                # 首先检查文件是否为空
                if uploaded_file.size == 0:
                    st.error("上传的文件为空！")
                    st.stop()

                # 尝试读取文件
                df = pd.read_csv(uploaded_file)

                # 验证数据格式
                required_columns = ['date', 'weight']
                if all(col in df.columns for col in required_columns):
                    # 转换日期格式
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    # 删除无效的日期行
                    df = df.dropna(subset=['date'])

                    if len(df) == 0:
                        st.error("文件中没有有效的日期数据！")
                        st.stop()

                    # 合并数据
                    if not st.session_state.df.empty:
                        st.session_state.df = pd.concat([st.session_state.df, df]).drop_duplicates(subset=['date'])
                    else:
                        st.session_state.df = df

                    st.session_state.df = st.session_state.df.sort_values('date')
                    st.success("成功导入数据！")
                    # 保存更新后的数据
                    user_manager.save_user_data()

                    # 显示导入的数据预览
                    with st.expander("查看导入的数据"):
                        st.dataframe(df.head())
                else:
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    st.error(f"文件格式错误，缺少以下必要列：{', '.join(missing_cols)}")
                    st.info(f"文件包含的列：{', '.join(df.columns.tolist())}")

            except pd.errors.EmptyDataError:
                st.error("文件为空或没有有效的CSV数据！")
            except pd.errors.ParserError:
                st.error("CSV文件格式错误，无法解析！")
            except UnicodeDecodeError:
                # 尝试不同的编码
                try:
                    uploaded_file.seek(0)  # 重置文件指针
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                    # 继续验证逻辑...
                except Exception as e:
                    st.error(f"文件编码错误：{str(e)}")
            except Exception as e:
                st.error(f"数据导入失败：{str(e)}")


    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<span class="lxh-subtle">🐾 今日打卡一下下，悄悄变更好～</span>', unsafe_allow_html=True)
    # 在每个tab的末尾添加自动保存
    for tab in tabs:
        # 在tab内容结束后添加
        user_manager.save_user_data()

# ============ 趋势分析 =============
with tabs[2]:
    df = st.session_state.df.copy()
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("## <span class='small-icon'>📈</span> 体重趋势", unsafe_allow_html=True)
            draw_picture.plot_weight_trend(df, st.session_state.target_weight)
        with col2:
            st.markdown("## <span class='small-icon'>🔥</span> 热量收支", unsafe_allow_html=True)
            draw_picture.plot_calorie_balance(df)
    else:
        st.info("暂无数据，先添加记录吧~")
    # 在每个tab的末尾添加自动保存
    for tab in tabs:
        # 在tab内容结束后添加
        user_manager.save_user_data()
# ============ 体重预测 =============
with tabs[3]:
    st.header("🔮 体重预测")

    # 设置预测天数
    pred_days = st.slider("预测天数", 7, 90, 28, 7, key="pred_days_slider")

    if st.session_state.df is None or len(st.session_state.df) < 10:
        st.warning(
            f"请先录入至少10条体重数据后再进行预测，当前只有{len(st.session_state.df) if st.session_state.df is not None else 0}条数据")
    else:
        # 导入必要的函数
        from models import load_lstm, train_lstm, predict_future_lstm

        # 加载模型
        model, scalers = load_lstm()

        # 进行预测
        with st.spinner("正在进行预测计算..."):
            pred = predict_future_lstm(
                st.session_state.df,
                model,
                scalers,
                pred_days,
                st.session_state.user_training_plan,
                st.session_state.diet_plan
            )

        if pred['status'] != 'success':
            st.error(pred['message'])
            st.stop()

        # 显示预测结果
        st.success("预测完成！")

        # 结果显示
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("当前体重", f"{pred['start_weight']:.2f} kg")
        with col2:
            st.metric(f"{pred_days}天后体重", f"{pred['end_weight']:.2f} kg")
        with col3:
            change = pred['weight_change']
            st.metric("预计变化", f"{change:+.1f} kg",
                      delta_color="inverse" if change > 0 else "normal")
        with col4:
            daily_change = change / pred_days
            st.metric("日均变化", f"{daily_change:+.2f} kg/天")

        # 绘制预测图表
        fig, ax = plt.subplots(figsize=(14, 7))
        # 历史数据
        hist_df = st.session_state.df.copy().sort_values('date')
        if len(hist_df) > 90:
            hist_df = hist.tail(90)
        ax.plot(hist_df['date'], hist_df['weight'],
                marker='o', markersize=4, linewidth=2,
                color='#1f77b4', label="历史体重", alpha=0.8)
        # 预测数据
        pred_dates = [p['date'] for p in pred['predictions']]
        pred_weights = [p['weight'] for p in pred['predictions']]
        ax.plot(pred_dates, pred_weights,
                marker='s', markersize=5, linewidth=2, linestyle='--',
                color='#ff7f0e', label="预测体重", alpha=0.8)
        # 目标线
        if st.session_state.target_weight is not None:
            target_weight = st.session_state.target_weight
            ax.axhline(y=target_weight, color='red', linestyle=':', linewidth=2,
                       alpha=0.7, label=f'目标体重: {target_weight}kg')
        # 分隔线
        last_hist_date = hist_df['date'].iloc[-1]
        ax.axvline(x=last_hist_date, color='gray', linestyle='--', alpha=0.6, linewidth=1)
        # 图表样式
        ax.set_title(f"体重预测 ({pred_days}天)", fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('体重 (kg)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend(loc='upper right', fontsize=10)
        # Y轴范围
        all_weights = list(hist_df['weight']) + pred_weights
        if st.session_state.target_weight is not None:
            all_weights.append(st.session_state.target_weight)
        if all_weights:
            min_weight = min(all_weights)
            max_weight = max(all_weights)
            padding = (max_weight - min_weight) * 0.15
            ax.set_ylim(min_weight - padding, max_weight + padding)

        fig.autofmt_xdate(rotation=45)
        st.pyplot(fig)

        # 个性化建议
        st.markdown("### 💡 个性化建议")
        recommendation.export_report(pred, st.session_state.target_weight)
    # 在每个tab的末尾添加自动保存
    for tab in tabs:
        # 在tab内容结束后添加
        user_manager.save_user_data()
# ============ 个人设置 =============
with tabs[4]:
    # 基本信息设置
    st.markdown("### 基本信息")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.user_height = st.number_input(
            "身高(cm)",
            min_value=50.0,
            max_value=250.0,
            value=st.session_state.user_height,
            step=0.1,
            help="请输入您的身高"
        )
        st.session_state.user_sex = st.radio(
            "性别",
            ["男", "女"],
            index=0 if st.session_state.user_sex == "男" else 1
        )
    with col2:
        st.session_state.user_age = st.number_input(
            "年龄",
            min_value=10,
            max_value=100,
            value=st.session_state.user_age,
            step=1,
            help="请输入您的年龄"
        )
        st.session_state.user_activity_level = st.selectbox(
            "活动水平",
            ["久坐", "轻度活动", "中度活动", "高强度活动", "非常活跃"],
            index=["久坐", "轻度活动", "中度活动", "高强度活动", "非常活跃"].index(
                st.session_state.user_activity_level)
        )

    # 目标体重设置
    st.markdown("---")
    st.markdown("### 目标设置")

    st.session_state.target_weight = st.number_input(
        "🎯 目标体重(kg)",
        min_value=30.0,
        max_value=150.0,
        value=st.session_state.target_weight if st.session_state.target_weight is not None else 60.0,
        step=0.1,
        help="设置目标体重"
    )

    if st.button("💾 保存目标体重", key="save_target"):
        st.session_state.target_baseline_weight = float(
            st.session_state.df['weight'].iloc[-1]) if not st.session_state.df.empty else None
        st.session_state.target_set_date = datetime.date.today()
        user_manager.save_user_data()
        st.success("保存成功！")

    # 锻炼计划设置 - 确保这个部分显示
    st.markdown("---")
    st.markdown("### 锻炼计划")

    # 添加新的锻炼项目
    col_ex1, col_ex2, col_ex3 = st.columns(3)

    with col_ex1:
        new_exercise_type = st.selectbox("运动类型", list(DATA.EXERCISE_Kkcal.keys()), key="new_exercise_type")
    with col_ex2:
        new_exercise_time = st.number_input("时长(分钟)", min_value=0, max_value=240, value=30, key="new_exercise_time")
    with col_ex3:
        new_days_per_week = st.number_input("每周天数", min_value=1, max_value=7, value=3, key="new_days_per_week")

    if st.button("➕ 添加锻炼项目", key="add_exercise_item"):
        new_item = pd.DataFrame([{
            'exercise_type': new_exercise_type,
            'exercise_time': new_exercise_time,
            'days_per_week': new_days_per_week
        }])

        if st.session_state.user_training_plan is None or st.session_state.user_training_plan.empty:
            st.session_state.user_training_plan = new_item
        else:
            st.session_state.user_training_plan = pd.concat([st.session_state.user_training_plan, new_item],
                                                            ignore_index=True)
        user_manager.save_user_data()
        st.success("锻炼项目已添加！")
        st.rerun()

    # 显示当前锻炼计划
    if st.session_state.user_training_plan is not None and len(st.session_state.user_training_plan) > 0:
        st.info("当前锻炼计划:")

        # 为每个计划添加删除按钮
        for index, row in st.session_state.user_training_plan.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.write(f"**{row['exercise_type']}**")
            with col2:
                st.write(f"{int(row['exercise_time'])} 分钟")
            with col3:
                st.write(f"每周 {int(row['days_per_week'])} 天")
            with col4:
                # 为每个计划添加单独的删除按钮
                if st.button("🗑️", key=f"delete_exercise_{index}"):
                    # 删除该行
                    st.session_state.user_training_plan = st.session_state.user_training_plan.drop(index).reset_index(
                        drop=True)
                    # 如果删除后为空，设置为None
                    if len(st.session_state.user_training_plan) == 0:
                        st.session_state.user_training_plan = None
                    user_manager.save_user_data()
                    st.success(f"已删除 {row['exercise_type']} 计划")
                    st.rerun()

        # 添加清除所有计划的按钮
        if st.button("🗑️ 清除所有锻炼计划", key="clear_all_plan"):
            st.session_state.user_training_plan = None
            user_manager.save_user_data()
            st.success("所有锻炼计划已清除！")
            st.rerun()
    else:
        st.info("暂无锻炼计划，请添加新的锻炼项目。")
    # 在每个tab的末尾添加自动保存
    for tab in tabs:
        # 在tab内容结束后添加
        user_manager.save_user_data()
    # ========== 饮食计划管理 ==========
    st.markdown("---")
    st.markdown("### 饮食计划")

    # 添加预设减脂餐计划选择
    st.markdown("#### 🍽️ 选择预设减脂餐计划")

    # 创建三个列来并排显示减脂餐选项
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander("🥗 经典减脂餐", expanded=False):
            st.markdown("**餐单内容:**")
            st.markdown("""
            - 🍳 早餐: 燕麦50g + 鸡蛋100g
            - 🍗 午餐: 鸡胸肉150g + 糙米100g + 西兰花200g  
            - 🐟 晚餐: 三文鱼120g + 红薯100g
            - 🥛 加餐: 希腊酸奶100g
            """)
            st.markdown("**特点:** 均衡营养，适合大多数人")
    with col2:
        with st.expander("🥑 低碳水减脂餐", expanded=False):
            st.markdown("**餐单内容:**")
            st.markdown("""
            - 🍳 早餐: 鸡蛋120g + 牛油果50g
            - 🥩 午餐: 瘦牛肉150g + 菠菜200g
            - 🍗 晚餐: 鸡胸肉150g + 西兰花200g
            - 🥜 加餐: 坚果30g
            """)
            st.markdown("**特点:** 低碳水化合物，快速减脂")
    with col3:
        with st.expander("💪 高蛋白减脂餐", expanded=False):
            st.markdown("**餐单内容:**")
            st.markdown("""
            - 🥛 早餐: 希腊酸奶150g + 鸡蛋100g  
            - 🍗 午餐: 鸡胸肉200g + 糙米80g
            - 🧈 晚餐: 豆腐200g + 蔬菜沙拉250g
            """)
            st.markdown("**特点:** 高蛋白，增肌减脂")

    col_search, col_blank = st.columns([3, 1])
    with col_search:
        diet_food_query = st.text_input("搜索要添加到饮食计划的食物", key="diet_food_query_settings")
    with col_blank:
        st.write("")

    # 搜索按钮
    if st.button("🔍 搜索", key="diet_search_settings") and diet_food_query:
        search_results = Plan.search_food(diet_food_query)

        if search_results:
            st.session_state.found_food = search_results
            st.success(f"找到 {len(search_results)} 个结果")
        else:
            st.warning("未找到相关食物，请尝试其他关键词。")

    preset_plan = st.selectbox(
        "选择预设减脂餐计划",
        list(DATA.PRESET_DIET_PLANS.keys()) + ["自定义"],
        help="选择预设的减脂餐计划或自定义饮食"
    )

    if preset_plan != "自定义" and st.button("📋 加载预设计划", key="load_preset_plan"):
        Plan.load_preset_plan(preset_plan)

    # 显示找到的食物并让用户选择
    if "found_food" in st.session_state and st.session_state.found_food:
        options = [
            f"{food['brand']} - {food['name']} ({food['calories']} kcal/100g)"
            for food in st.session_state.found_food
        ]

        idx = st.selectbox("选择要加入计划的食物", range(len(options)),
                           format_func=lambda i: options[i], key="diet_select_settings")
        chosen = st.session_state.found_food[idx]

        qty = st.number_input("计划每次摄入量 (g)", min_value=1, max_value=2000,
                              value=100, step=10, key="diet_qty_settings")
        meal = st.selectbox("所属餐次", ["早餐", "午餐", "晚餐", "加餐"],
                            index=0, key="diet_meal_settings")
        days_week = st.number_input("每周几次", min_value=1, max_value=7,
                                    value=7, step=1, key="diet_days_settings")

        est_kcal = chosen['calories'] * (qty / 100)
        st.metric("估算每次热量", f"{est_kcal:.0f} kcal")

        if st.button("➕ 添加到饮食计划", key="add_to_diet_settings"):
            entry = {
                'meal': meal,
                'name': chosen['name'],
                'brand': chosen['brand'],
                'quantity': qty,
                'unit': chosen.get('unit', 'g'),
                'calories': chosen['calories'],
                'protein': chosen.get('protein', 0),
                'carbs': chosen.get('carbs', 0),
                'fat': chosen.get('fat', 0),
                'days_per_week': int(days_week)
            }
            st.session_state.diet_plan = pd.concat([st.session_state.diet_plan,
                                                    pd.DataFrame([entry])], ignore_index=True)
            user_manager.save_user_data()
            st.success("已添加到饮食计划！")

    # 显示当前饮食计划
    if not st.session_state.diet_plan.empty:
        st.markdown("#### 📊 当前饮食计划统计")

        # 计算每日营养总量
        daily_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }
        for _, row in st.session_state.diet_plan.iterrows():
            if 'calories' in row and 'days_per_week' in row:
                daily_factor = row['days_per_week'] / 7
                quantity_factor = row['quantity'] / 100

                daily_nutrition['calories'] += row['calories'] * quantity_factor * daily_factor
                daily_nutrition['protein'] += row.get('protein', 0) * quantity_factor * daily_factor
                daily_nutrition['carbs'] += row.get('carbs', 0) * quantity_factor * daily_factor
                daily_nutrition['fat'] += row.get('fat', 0) * quantity_factor * daily_factor

        # 显示每日营养统计
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("日均热量", f"{daily_nutrition['calories']:.0f} kcal")
        with col2:
            st.metric("日均蛋白质", f"{daily_nutrition['protein']:.1f} g")
        with col3:
            st.metric("日均碳水", f"{daily_nutrition['carbs']:.1f} g")
        with col4:
            st.metric("日均脂肪", f"{daily_nutrition['fat']:.1f} g")

        st.markdown("#### 📝 饮食计划详情")
        display_plan = st.session_state.diet_plan.copy()
        st.dataframe(display_plan, use_container_width=True, key="diet_plan_table_settings")

        if st.button("🗑️ 清空饮食计划", key="clear_diet_plan_button_2024_unique_final_12345"):
            st.session_state.diet_plan = st.session_state.diet_plan.iloc[0:0]
            user_manager.save_user_data()
            st.success("饮食计划已清空。")

    # 在每个tab的末尾添加自动保存
    for tab in tabs:
        # 在tab内容结束后添加
        user_manager.save_user_data()

# 页脚
# 在页面底部添加登出按钮
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🚪 退出登录", key="logout_btn"):
        user_manager.logout()
        st.rerun()

