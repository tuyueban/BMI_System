import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        :root {
            /* 颜色变量 */
            --primary-color: #4cc9f0;
            --primary-dark: #4361ee;
            --secondary-color: #f72585;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --gray-color: #6c757d;
            --border-color: #dee2e6;

            /* 尺寸变量 */
            --border-radius-sm: 8px;
            --border-radius-md: 12px;
            --border-radius-lg: 16px;
            --box-shadow-sm: 0 2px 6px rgba(0,0,0,0.1);
            --box-shadow-md: 0 4px 12px rgba(0,0,0,0.08);
            --box-shadow-lg: 0 6px 16px rgba(0,0,0,0.12);
        }

        /* 响应式调整 */
        @media (max-width: 768px) {
            :root {
                --font-size-sm: 0.875rem;
                --font-size-md: 1rem;
                --font-size-lg: 1.25rem;
            }
        }

        @media (min-width: 769px) {
            :root {
                --font-size-sm: 0.9375rem;
                --font-size-md: 1.125rem;
                --font-size-lg: 1.5rem;
            }
        }

        /* 主容器样式 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max-width: 1200px;
        }

        /* 卡片样式优化 */
        .stMetric {
            background: linear-gradient(135deg, var(--light-color) 0%, #e9ecef 100%);
            border-radius: var(--border-radius-lg);
            padding: 20px;
            box-shadow: var(--box-shadow-md);
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }

        /* 自定义卡片组件 */
        .custom-card {
            background: white;
            border-radius: var(--border-radius-lg);
            padding: 20px;
            box-shadow: var(--box-shadow-md);
            border: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }

        .custom-card:hover {
            transform: translateY(-3px);
            box-shadow: var(--box-shadow-lg);
            border-color: rgba(76, 201, 240, 0.3);
        }

        /* 进度指示器 */
        .progress-container {
            width: 100%;
            background-color: #e9ecef;
            border-radius: var(--border-radius-sm);
            margin: 1rem 0;
        }

        .progress-bar {
            height: 8px;
            border-radius: var(--border-radius-sm);
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-dark) 100%);
            transition: width 0.5s ease-in-out;
        }

        .stMetric:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        }

        /* 按钮样式优化 */
        .stButton > button {
            border-radius: var(--border-radius-md);
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s ease;
            border: none;
            box-shadow: var(--box-shadow-sm);
            background-color: var(--primary-color);
            color: white;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }

        /* 输入框样式优化 */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            border-radius: 10px;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            transition: border-color 0.2s ease;
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #4cc9f0;
            box-shadow: 0 0 0 3px rgba(76, 201, 240, 0.1);
        }

        /* 标签页样式优化 */
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
            padding: 1rem 1.5rem;
            border-radius: 8px 8px 0 0;
            margin: 0 0.2rem;
            background: #f8f9fa;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: #e9ecef;
        }

        .stTabs [aria-selected="true"] {
            background: #ffffff;
            color: #4cc9f0;
            box-shadow: 0 -2px 0 #4cc9f0 inset;
        }

        /* 数据表格样式优化 */
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        /* 进度条样式优化 */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #4cc9f0 0%, #4361ee 100%);
            border-radius: 8px;
        }

        /* 警告和信息框样式 */
        .stAlert {
            border-radius: 12px;
            padding: 1rem;
            border-left: 4px solid;
        }

        /* 自定义成功提示 */
        .success-alert {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left-color: #28a745;
        }

        /* 加载动画 */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .pulse {
            animation: pulse 2s infinite;
        }
        .small-icon {
            font-size: 0.7em;
        }
    </style>
    """, unsafe_allow_html=True)

def create_page_header(title, description=None, icon="📊"):
    st.markdown(f"# <span class='small-icon'>{icon}</span> {title}", unsafe_allow_html=True)
    if description:
        st.markdown(f"<p style='color: #6c757d; margin-top: -0.5rem; margin-bottom: 2rem;'>{description}</p>",
                        unsafe_allow_html=True)
    st.markdown("---")

def create_metric_card(title, value, delta=None, delta_color="normal", icon=None, progress=None, progress_max=100):
    # 构建卡片内容
    card_content = []

    # 添加图标和标题行
    title_line = []
    if icon:
        title_line.append(f"<span class='small-icon'>{icon}</span> ")
    title_line.append(f"<strong>{title}</strong>")
    card_content.append(
        f"<div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;'>{''.join(title_line)}</div>")

    # 添加数值
    card_content.append(f"<div style='font-size: 2rem; font-weight: 700;'>{value}</div>")

    # 添加变化量
    if delta is not None:
        delta_color_map = {
            "normal": "#6c757d",
            "inverse": "#6c757d",
            "off": "#6c757d",
            "success": "var(--success-color)",
            "error": "var(--danger-color)"
        }
        delta_color = delta_color_map.get(delta_color, delta_color)
        card_content.append(f"<div style='color: {delta_color}; display: flex; align-items: center;'>{delta}</div>")

    # 添加进度条
    if progress is not None:
        progress_percent = min(max(0, progress), progress_max) / progress_max * 100
        card_content.append(f"<div class='progress-container'>")
        card_content.append(f"<div class='progress-bar' style='width: {progress_percent}%'></div>")
        card_content.append(f"</div>")
        card_content.append(
            f"<div style='display: flex; justify-content: space-between; font-size: 0.875rem; color: var(--gray-color);'>")
        card_content.append(f"<span>{progress}/{progress_max}</span>")
        card_content.append(f"<span>{progress_percent:.1f}%</span>")
        card_content.append(f"</div>")

    # 使用自定义卡片样式
    st.markdown(f"<div class='custom-card'>{''.join(card_content)}</div>", unsafe_allow_html=True)

def create_section_header(title, icon=None, color=None):
    """创建增强版章节标题，支持颜色和自定义样式"""
    style = []
    if color:
        style.append(f"color: {color};")
    style_str = '; '.join(style) if style else ''

    title_content = []
    if icon:
        title_content.append(f"<span class='small-icon'>{icon}</span> ")
    title_content.append(f"<span style='{style_str}'>{title}</span>")

    st.markdown(f"### {''.join(title_content)}", unsafe_allow_html=True)
    st.markdown(
        "<div style='height: 3px; background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-dark) 100%); border-radius: 3px; margin: 0.5rem 0 1.5rem 0;'></div>",
        unsafe_allow_html=True)

def create_info_box(message, type="info", dismissible=False):
    """创建增强版信息提示框，支持可关闭功能和自定义样式"""
    icon_map = {
        "info": ("ℹ️", "#4cc9f0", "var(--primary-color)"),
        "success": ("✅", "#28a745", "var(--success-color)"),
        "warning": ("⚠️", "#ffc107", "var(--warning-color)"),
        "error": ("❌", "#dc3545", "var(--danger-color)")
    }

    icon, color, css_var = icon_map.get(type, ("ℹ️", "#6c757d", "var(--gray-color)"))

    content = [
        f"<div style='display: flex; align-items: flex-start; padding: 1rem; border-radius: var(--border-radius-md); background: rgba({color.lstrip('#')}, 0.1); border-left: 4px solid {css_var};'>",
        f"<div class='small-icon' style='margin-right: 0.75rem;'>{icon}</div>",
        f"<div style='flex: 1;'>{message}</div>"
    ]

    content.append("</div>")

    st.markdown(''.join(content), unsafe_allow_html=True)

def create_success_toast(message):
    """创建成功提示"""
    st.markdown(f"<div class='small-icon'>✅</div> {message}", unsafe_allow_html=True)
    return

def create_loading_spinner(text="处理中..."):
    """创建统一的加载动画"""
    st.markdown(f"<div class='small-icon'>⏳</div> {text}", unsafe_allow_html=True)
    return

def create_expandable_section(title, content, expanded=False, icon=None):
    """创建增强版可展开章节，支持图标和自定义样式"""
    display_title = f"<span class='small-icon'>{icon}</span> {title}" if icon else title

    with st.expander(display_title, expanded=expanded):
        st.markdown(
            "<div class='custom-card' style='box-shadow: none; border-radius: var(--border-radius-md); margin-bottom: 0;'>",
            unsafe_allow_html=True)
        if callable(content):
            content()
        else:
            st.write(content)
        st.markdown("</div>", unsafe_allow_html=True)

def create_form_section(title, description=None):
    """创建表单区域"""
    st.markdown(f"### {title}")
    if description:
        st.markdown(f"<p style='color: #6c757d; margin-top: -0.5rem; margin-bottom: 1rem;'>{description}</p>",
                   unsafe_allow_html=True)

def create_data_section(title, description=None):
    """创建数据展示区域"""
    st.markdown(f"#### {title}")
    if description:
        st.markdown(f"<p style='color: #6c757d; margin-top: -0.5rem; margin-bottom: 1rem;'>{description}</p>",
                   unsafe_allow_html=True)

def create_footer():
    """创建页脚"""
    st.markdown("""
    <div class="footer">
        <hr style="margin: 2rem auto; width: 50%;">
        <p>BMI体质评估与预测系统</p>
        <p style="font-size: 0.8rem; opacity: 0.7;">记录健康数据，预见更好的自己</p>
    </div>
    """, unsafe_allow_html=True)




