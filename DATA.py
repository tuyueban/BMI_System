import os

BMR_COEFFICIENT = 1.3
EXERCISE_Kkcal = {
    '无': 0,   #/分钟
    '散步': 3.6,
    '跑步': 8.4,
    '游泳': 7.2,
    '骑自行车': 5.4,
    '跳绳': 10.8,
    '篮球': 6.2
}

MODEL_FILE = "weight_prediction_lstm.h5"
SCALER_FILE = "scalers.pkl"
DATA_FILE = "health_data.csv"

OPENFOODFACTS_API_URL = "https://world.openfoodfacts.org/api/v2/search"
NUTRIENT_KEYS = {
    'energy-kcal': '能量 (kcal)',
    'fat': '脂肪 (g)',
    'saturated-fat': '饱和脂肪 (g)',
    'carbohydrates': '碳水化合物 (g)',
    'sugars': '糖 (g)',
    'proteins': '蛋白质 (g)',
    'fiber': '膳食纤维 (g)',
    'sodium': '钠 (mg)'
}
PRESET_DIET_PLANS = {
    "经典减脂餐": [
        {"meal": "早餐", "name": "燕麦", "quantity": 50, "days_per_week": 7},
        {"meal": "早餐", "name": "鸡蛋", "quantity": 100, "days_per_week": 7},
        {"meal": "午餐", "name": "鸡胸肉", "quantity": 150, "days_per_week": 7},
        {"meal": "午餐", "name": "糙米", "quantity": 100, "days_per_week": 7},
        {"meal": "午餐", "name": "西兰花", "quantity": 200, "days_per_week": 7},
        {"meal": "晚餐", "name": "三文鱼", "quantity": 120, "days_per_week": 7},
        {"meal": "晚餐", "name": "红薯", "quantity": 100, "days_per_week": 7},
        {"meal": "加餐", "name": "希腊酸奶", "quantity": 100, "days_per_week": 7}
    ],
    "低碳水减脂餐": [
        {"meal": "早餐", "name": "鸡蛋", "quantity": 120, "days_per_week": 7},
        {"meal": "早餐", "name": "牛油果", "quantity": 50, "days_per_week": 7},
        {"meal": "午餐", "name": "瘦牛肉", "quantity": 150, "days_per_week": 7},
        {"meal": "午餐", "name": "菠菜", "quantity": 200, "days_per_week": 7},
        {"meal": "晚餐", "name": "鸡胸肉", "quantity": 150, "days_per_week": 7},
        {"meal": "晚餐", "name": "西兰花", "quantity": 200, "days_per_week": 7},
        {"meal": "加餐", "name": "坚果", "quantity": 30, "days_per_week": 7}
    ],
    "高蛋白减脂餐": [
        {"meal": "早餐", "name": "希腊酸奶", "quantity": 150, "days_per_week": 7},
        {"meal": "早餐", "name": "鸡蛋", "quantity": 100, "days_per_week": 7},
        {"meal": "午餐", "name": "鸡胸肉", "quantity": 200, "days_per_week": 7},
        {"meal": "午餐", "name": "糙米", "quantity": 80, "days_per_week": 7},
        {"meal": "晚餐", "name": "豆腐", "quantity": 200, "days_per_week": 7},
        {"meal": "晚餐", "name": "蔬菜沙拉", "quantity": 250, "days_per_week": 7}
    ]
}
DIET_FOODS_DATABASE = {
    # 蛋白质类
    "鸡胸肉": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "unit": "100g"},
    "鸡蛋": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "unit": "100g"},
    "三文鱼": {"calories": 208, "protein": 20, "carbs": 0, "fat": 13, "unit": "100g"},
    "瘦牛肉": {"calories": 250, "protein": 26, "carbs": 0, "fat": 15, "unit": "100g"},
    "豆腐": {"calories": 76, "protein": 8, "carbs": 2, "fat": 4, "unit": "100g"},
    "希腊酸奶": {"calories": 59, "protein": 10, "carbs": 3.6, "fat": 0.4, "unit": "100g"},

    # 碳水类
    "糙米": {"calories": 111, "protein": 2.6, "carbs": 23, "fat": 0.9, "unit": "100g"},
    "燕麦": {"calories": 389, "protein": 16.9, "carbs": 66, "fat": 6.9, "unit": "100g"},
    "全麦面包": {"calories": 265, "protein": 13, "carbs": 41, "fat": 3.5, "unit": "100g"},
    "红薯": {"calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "unit": "100g"},
    "藜麦": {"calories": 120, "protein": 4.4, "carbs": 21, "fat": 1.9, "unit": "100g"},
    "坚果": {"calories": 580, "protein": 20, "carbs": 20, "fat": 50, "unit": "100g"},
    # 蔬菜类
    "西兰花": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "unit": "100g"},
    "菠菜": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "unit": "100g"},
    "胡萝卜": {"calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "unit": "100g"},
    "黄瓜": {"calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1, "unit": "100g"},
    "西红柿": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "unit": "100g"},
    "牛油果": {"calories": 160, "protein": 2, "carbs": 9, "fat": 15, "unit": "100g"},
    "蔬菜沙拉": {"calories": 15, "protein": 0.5, "carbs": 3, "fat": 0.1, "unit": "100g"}
}


USER_DATA_DIR = "user_data"

# 确保用户目录存在
os.makedirs(USER_DATA_DIR, exist_ok=True)

def get_user_file(username, filename):
    """获取用户特定的文件路径"""
    if username is None:
        # 如果没有用户，使用默认路径（兼容旧版本）
        return filename
    user_dir = os.path.join(USER_DATA_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, filename)

# 修改为函数形式，而不是在导入时执行
def get_data_file(username=None):
    return get_user_file(username, "health_data.csv")

def get_model_file(username=None):
    return get_user_file(username, "weight_prediction_lstm.h5")

def get_scaler_file(username=None):
    return get_user_file(username, "scalers.pkl")

# 用户配置文件
def get_user_config_file(username=None):
    return get_user_file(username, "user_config.pkl")