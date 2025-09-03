#建议函数

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import bmi_calculation
import DATA


def export_report(data, target_weight=None):
    """生成健康报告，支持历史数据和预测结果"""

    # 检查数据类型
    if isinstance(data, pd.DataFrame):
        # 处理历史数据
        if data.empty:
            st.info("暂无数据")
            return


    elif isinstance(data, dict) and data.get('status') == 'success':
        if target_weight is not None:
            current_to_target = data['end_weight'] - target_weight
            if abs(current_to_target) < 0.5:
                st.success("🎉 预测显示您将接近目标体重！继续保持当前计划。")
            elif current_to_target > 0:
                st.warning("⚠️ 预测显示仍需减重，建议适当增加运动或调整饮食。")
            else:
                st.info("ℹ️ 预测显示体重偏低，建议适当增加营养摄入。")

        # 检查减重速率是否健康
        if 'predictions' in data and len(data['predictions']) > 1:
            days = len(data['predictions'])
            total_change = data['weight_change']
            weekly_change = abs(total_change) / days * 7

            if weekly_change > 1.0:
                st.warning("⚠️ 预测减重速率过快，建议调整为每周0.5-1kg的健康范围。")
            elif 0.5 <= weekly_change <= 1.0:
                st.success("✅ 预测减重速率在健康范围内。")
            else:
                st.info("ℹ️ 预测减重速率较慢，可能需要调整计划。")

    else:
        st.warning("无法生成报告：数据格式不支持")

def generate_recommendation(pred, target_weight):
    """生成基于计划的增强建议"""
    if target_weight is None:
        st.info("📝 请先在'个人设置'中设置目标体重，获取更精准的建议")
        return

    end_weight = pred['end_weight']
    target_diff = end_weight - target_weight
    start_weight = pred['start_weight']

    # 获取用户基本信息
    user_height = st.session_state.user_height
    user_age = st.session_state.user_age
    user_sex = st.session_state.user_sex

    if abs(target_diff) < 0.5:
        st.success("🎉 完美！按照当前计划，您将几乎达成目标体重！")
        st.info("""
        - 继续保持当前的计划和习惯
        - 定期监测体重变化
        - 维持健康的生活方式
        """)
        return

    # 分析预测数据
    preds_df = pd.DataFrame(pred['predictions'])

    # 检查必要的列是否存在，如果不存在就使用默认值
    if 'total_calorie_burn' not in preds_df.columns:
        # 如果没有总消耗数据，就使用简单的估算
        avg_total_burn = preds_df['planned_exercise'].mean() + (DATA.BMR_COEFFICIENT * start_weight * 24)
        avg_basal_metabolism = DATA.BMR_COEFFICIENT * start_weight * 24
    else:
        avg_total_burn = preds_df['total_calorie_burn'].mean()
        avg_basal_metabolism = preds_df[
            'basal_metabolism'].mean() if 'basal_metabolism' in preds_df.columns else DATA.BMR_COEFFICIENT * start_weight * 24

    avg_exercise = preds_df['planned_exercise'].mean()
    avg_intake = preds_df['planned_calories'].mean()
    daily_balance = avg_intake - avg_total_burn

    # 显示正确的消耗分析
    st.info(f"📊 计划分析: 日均总消耗 {avg_total_burn:.0f} kcal "
            f"(基础代谢 {avg_basal_metabolism:.0f} kcal + 运动 {avg_exercise:.0f} kcal)")
    st.info(f"🍽️ 日均摄入: {avg_intake:.0f} kcal")
    st.info(f"⚖️ 日均热量平衡: {daily_balance:+.0f} kcal")

    # 使用科学BMR计算TDEE
    current_bmr = bmi_calculation.calculate_bmr(start_weight, user_height, user_age, user_sex)

    activity_levels = {
        "久坐": 1.2, "轻度活动": 1.375, "中度活动": 1.55,
        "高强度活动": 1.725, "非常活跃": 1.9
    }
    activity_factor = activity_levels.get(st.session_state.user_activity_level, 1.375)
    tdee = current_bmr * activity_factor

    st.info(f"🔥 您的每日总能量消耗约为: {tdee:.0f} kcal")

    if target_diff > 0:  # 需要减重
        st.warning(f"⚠️ 当前计划下，预计距离目标还有 {target_diff:.1f}kg 差距")

        # 健康减重建议
        days_to_goal = len(preds_df)
        healthy_weekly_loss = 0.5  # 每周健康减重0.5kg
        healthy_daily_deficit = (healthy_weekly_loss * 7700) / 7  # 约550 kcal/天

        total_deficit_needed = target_diff * 7700
        actual_daily_deficit = total_deficit_needed / days_to_goal

        # 判断减重速度是否合理
        is_too_fast = False
        if actual_daily_deficit > healthy_daily_deficit * 1.5:  # 超过825 kcal/天
            st.warning("⚠️ 当前减重速度可能过快，建议调整计划")
            recommended_deficit = healthy_daily_deficit
            is_too_fast = True
        elif actual_daily_deficit > healthy_daily_deficit:  # 550-825 kcal/天
            st.info("💡 当前减重速度较快但仍可接受")
            recommended_deficit = actual_daily_deficit
        else:  # 小于550 kcal/天
            st.success("✅ 当前减重速度在健康范围内")
            recommended_deficit = actual_daily_deficit

        st.info(f"💡 建议每日热量缺口: {recommended_deficit:.0f} kcal")

        # 给出具体建议
        st.info("💪 **优化建议:**")

        if is_too_fast:
            # 减重速度过快的建议
            excess_deficit = actual_daily_deficit - healthy_daily_deficit
            st.write(f"- ⚠️ 减重速度过快，建议减少 {excess_deficit:.0f} kcal 的每日热量缺口")
            st.write("- 🍽️ 适当增加摄入量，确保营养均衡")
            st.write("- 🏃‍♂️ 保持适度运动，不要过度锻炼")
            st.write("- ⏳ 健康减重需要时间，建议调整为每周减重0.5kg")
        else:
            # 正常减重建议
            if daily_balance > -recommended_deficit:
                needed_adjustment = abs(daily_balance) - recommended_deficit
                st.write(f"- 需要再减少 {needed_adjustment:.0f} kcal 摄入或增加等量运动")
            else:
                st.write("- ✅ 当前计划的热量缺口适中，请继续保持")

        # 通用饮食建议
        st.info("🍽️ **饮食建议:**")
        st.write("- 增加蛋白质摄入，减少精制碳水化合物")
        st.write("- 多吃蔬菜水果，增加饱腹感")
        st.write("- 控制晚餐热量，避免夜宵")

    else:  # 需要增重
        st.info("🍽️ **调整建议:**")
        st.write("- 适当减少高热量食物摄入")
        st.write("- 保持运动量，但调整饮食结构")
        st.write("- 咨询营养师调整饮食计划")
        st.write("- 增加力量训练，促进肌肉生长而非脂肪堆积")

def generate_current_recommendation(df, target_weight):
    """基于当前状态生成建议，而不是预测"""
    if ('df' in locals() and df.empty) or target_weight is None:
        return "请先设置目标体重并记录数据"

    latest = df.iloc[-1]
    current_weight = latest['weight']
    weight_diff = current_weight - target_weight

    if abs(weight_diff) < 0.5:
        return "🎉 恭喜！您已接近目标体重，请继续保持"
    elif weight_diff > 0:
        return f"💪 需要减重 {weight_diff:.1f}kg，建议控制饮食并增加运动"
    else:
        return f"💪 需要增重 {abs(weight_diff):.1f}kg，建议增加蛋白质摄入和力量训练"


