import pickle
import pandas as pd
import os
import streamlit as st
import DATA


class UserManager:
    def __init__(self):
        self.current_user = None

    def login(self, username):
        """用户登录"""
        self.current_user = username
        st.session_state.current_user = username
        self.load_user_data()

    def logout(self):
        """用户登出"""
        self.current_user = None
        st.session_state.current_user = None
        st.session_state.user_initialized = False

    def user_exists(self, username):
        """检查用户是否存在"""
        user_dir = os.path.join(DATA.USER_DATA_DIR, username)
        return os.path.exists(user_dir)

    def create_user(self, username, user_config):
        """创建新用户"""
        user_dir = os.path.join(DATA.USER_DATA_DIR, username)
        os.makedirs(user_dir, exist_ok=True)

        # 保存用户配置
        config_file = DATA.get_user_config_file(username)
        with open(config_file, 'wb') as f:
            pickle.dump(user_config, f)

        # 创建空的数据文件
        empty_df = pd.DataFrame(columns=[
            'date', 'weight', 'height', 'exercise_type',
            'exercise_time', 'calorie_intake'
        ])
        empty_df.to_csv(DATA.get_data_file(username), index=False)

    def load_user_data(self):
        """加载用户数据到session_state"""
        if not self.current_user:
            return

        # 加载用户配置
        config_file = DATA.get_user_config_file(self.current_user)
        if os.path.exists(config_file):
            with open(config_file, 'rb') as f:
                user_config = pickle.load(f)

            # 设置session_state
            for key, value in user_config.items():
                st.session_state[key] = value

        # 加载健康数据
        data_file = DATA.get_data_file(self.current_user)
        if os.path.exists(data_file):
            st.session_state.df = pd.read_csv(data_file)
            st.session_state.df['date'] = pd.to_datetime(st.session_state.df['date'])
        else:
            st.session_state.df = pd.DataFrame(columns=[
                'date', 'weight', 'height', 'exercise_type',
                'exercise_time', 'calorie_intake'
            ])

        # 初始化其他用户特定的session_state
        st.session_state.user_initialized = True

    def save_user_data(self):
        """保存用户数据"""
        if not self.current_user:
            return

        # 保存用户配置
        user_config = {
            'user_height': st.session_state.get('user_height', 170.0),
            'user_sex': st.session_state.get('user_sex', "男"),
            'user_age': st.session_state.get('user_age', 30),
            'user_activity_level': st.session_state.get('user_activity_level', "轻度活动"),
            'target_weight': st.session_state.get('target_weight', None),
            'target_baseline_weight': st.session_state.get('target_baseline_weight', None),
            'target_set_date': st.session_state.get('target_set_date', None),
            'user_training_plan': st.session_state.get('user_training_plan', None),
            'diet_plan': st.session_state.get('diet_plan', pd.DataFrame())
        }

        config_file = DATA.get_user_config_file(self.current_user)
        with open(config_file, 'wb') as f:
            pickle.dump(user_config, f)

        # 保存健康数据
        if 'df' in st.session_state:
            st.session_state.df.to_csv(DATA.get_data_file(self.current_user), index=False)


# 创建全局用户管理器实例
user_manager = UserManager()