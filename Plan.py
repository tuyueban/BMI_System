#添加饮食计划和锻炼计划

import pandas as pd
import streamlit as st
import requests
import DATA

def validate_training_plan(plan_df, start_date, end_date):
    required_cols = ['date', 'exercise_type', 'exercise_time']
    if not all(col in plan_df.columns for col in required_cols):
        return False, "训练计划必须包含 'date', 'exercise_type', 'exercise_time' 列"

    plan_df['date'] = pd.to_datetime(plan_df['date'], errors='coerce')
    if plan_df['date'].isna().any():
        return False, "日期格式无效，请使用正确的日期格式"

    # 检查运动类型是否有效
    invalid_types = ~plan_df['exercise_type'].isin(DATA.EXERCISE_Kkcal.keys())
    if invalid_types.any():
        invalid = plan_df[invalid_types]['exercise_type'].unique()
        return False, f"无效的运动类型: {', '.join(invalid)}。有效类型: {', '.join(DATA.EXERCISE_Kkcal.keys())}"

    # 检查时间范围是否匹配预测天数
    plan_dates = plan_df['date'].sort_values()
    if plan_dates.min() < start_date or plan_dates.max() > end_date:
        return False, f"训练计划日期必须在预测范围内 ({start_date.date()} 至 {end_date.date()})"

    # 检查是否有重复日期
    if plan_df['date'].duplicated().any():
        return False, "训练计划中存在重复的日期"

    return True, "验证通过"

def get_planned_exercise(date, training_plan):
    """根据日期获取计划的运动类型和时间"""
    if training_plan is None or training_plan.empty:
        return 0

    day_of_week = date.dayofweek
    if day_of_week < len(training_plan):
        plan = training_plan.iloc[day_of_week % len(training_plan)]
        # 正确计算：运动强度(kcal/小时) × 时间(小时)
        return DATA.EXERCISE_Kkcal.get(plan['exercise_type'], 0) * (plan['exercise_time'] )
    return 0

def get_planned_calories(date, diet_plan):
    """根据日期获取计划的每日热量摄入"""
    if diet_plan.empty:
        return 0
    # 计算饮食计划的日均热量贡献
    daily_kcal = diet_plan.apply(
        lambda r: r['calories'] * (r['quantity'] / 100) * (r['days_per_week'] / 7),
        axis=1
    ).sum()
    return daily_kcal



def load_preset_plan(plan_name):
        """加载预设减脂餐计划"""
        plan_items = DATA.PRESET_DIET_PLANS[plan_name]
        new_plan_df = pd.DataFrame(plan_items)

        # 为每个食物添加营养信息
        for index, row in new_plan_df.iterrows():
            food_name = row['name']
            if food_name in DATA.DIET_FOODS_DATABASE:
                food_info = DATA.DIET_FOODS_DATABASE[food_name]
                new_plan_df.at[index, 'calories'] = food_info['calories']
                new_plan_df.at[index, 'protein'] = food_info['protein']
                new_plan_df.at[index, 'carbs'] = food_info['carbs']
                new_plan_df.at[index, 'fat'] = food_info['fat']
                new_plan_df.at[index, 'unit'] = food_info['unit']
                new_plan_df.at[index, 'brand'] = "预设减脂餐"

        st.session_state.diet_plan = new_plan_df
        st.success(f"已加载 {plan_name} 计划！")
        st.rerun()

def search_food(query):
        """搜索食物，先在本地数据库找，找不到再调用API"""
        results = []

        # 1. 先在本地数据库搜索
        for food_name, food_info in DATA.DIET_FOODS_DATABASE.items():
            if query.lower() in food_name.lower():
                results.append({
                    "name": food_name,
                    "brand": "减脂食物数据库",
                    "calories": food_info['calories'],
                    "protein": food_info['protein'],
                    "carbs": food_info['carbs'],
                    "fat": food_info['fat'],
                    "unit": food_info['unit']
                })

        # 2. 如果数据库中没有，再调用API搜索
        if not results:
            try:
                url = f"https://world.openfoodfacts.org/cgi/search.pl"
                params = {
                    "search_terms": query,
                    "search_simple": 1,
                    "action": "process",
                    "json": 1,
                    "page_size": 10
                }
                res = requests.get(url, params=params, timeout=8)
                data = res.json()

                if data.get("products"):
                    for product in data["products"]:
                        nutriments = product.get("nutriments", {})
                        calories = nutriments.get("energy-kcal_100g")
                        if calories is None:
                            energy_kj = nutriments.get("energy_100g")
                            calories = round(energy_kj / 4.184, 2) if energy_kj is not None else 0

                        results.append({
                            "name": product.get("product_name", "未知"),
                            "brand": product.get("brands", "未知"),
                            "calories": calories,
                            "protein": nutriments.get("proteins_100g", 0),
                            "carbs": nutriments.get("carbohydrates_100g", 0),
                            "fat": nutriments.get("fat_100g", 0),
                            "unit": "100g"
                        })
            except Exception as e:
                st.error(f"搜索失败: {e}")


        return results
