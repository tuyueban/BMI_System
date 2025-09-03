from typing import Tuple
import pandas as pd
import numpy as np

def calculate_bmi(weight: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    if height_m <= 0:
        return np.nan
    return round(weight / (height_m ** 2), 1)

def get_bmi_category(bmi: float) -> Tuple[str, str]:
    if pd.isna(bmi):
        return "未知", "请检查身高/体重输入是否有效。"
    if bmi < 18.5:
        return "偏瘦", "建议适当增加热量摄入，保持均衡饮食，适度运动增强体质。"
    elif 18.5 <= bmi < 24:
        return "正常", "恭喜！您的体重处于健康范围，请保持良好的饮食和运动习惯。"
    elif 24 <= bmi < 28:
        return "超重", "建议控制热量摄入，增加运动量，减少高脂肪、高糖食物的摄入。"
    else:
        return "肥胖", "建议咨询医生或营养师，制定科学的减重计划，增加有氧运动，严格控制饮食。"

def calculate_bmr(weight_kg, height_cm, age, sex):
    """使用Mifflin-St Jeor公式计算基础代谢率（更准确）"""
    if sex == "男":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


