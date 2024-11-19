import re
import pandas as pd
import streamlit as st
import time

# 页面设置
st.set_page_config(
    page_title="Sensor Info Verification",
    page_icon="⚙️",
    layout="wide",
)

# 添加自定义 CSS 样式
st.markdown(
    """
    <style>
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 1.5rem;
        font-weight: 600;
        color: #888;
        text-align: center;
        margin-bottom: 30px;
    }
    .green-text {
        color: #4CAF50; /* 设置统一的绿色 */
        font-weight: bold;
    }
    .blue-text {
        color: blue;
        font-weight: bold;
    }
    .red-text {
        color: red;
        font-weight: bold;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
    }
    /* 删除标题的绿色边框和背景 */
    h3 {
        border: none !important;
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def read_pm_file(pm_file):
    return pm_file.read().decode('utf-8')

def extract_configured_sensors(pm_content):
    pattern = re.compile(r'(\w+)\s*=>\s*{\s*"(\w+)"\s*=>\s*{configured\s*=>\s*"(\w+)"', re.IGNORECASE)
    matches = pattern.findall(pm_content)
    sensors_configured = [(match[0], match[1], match[2]) for match in matches]
    return sensors_configured

def read_excel_file(excel_file, sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    return df

def extract_creisrelevant_sensors(df):
    return df[['SensorName', 'CREISrelevant']].to_dict('records')

# 标题和说明
st.markdown('<div class="title">Sensor Info Verification</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Extra sensors will be marked in blue, Wrong configuration in red</div>', unsafe_allow_html=True)

# 上传文件部分
col1, col2 = st.columns(2)

with col1:
    pm_file = st.file_uploader("Upload .pm File", type=["pm"])
with col2:
    excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# 添加进度条
if pm_file or excel_file:
    progress_bar = st.progress(0)
    for i in range(1, 101):
        time.sleep(0.01)
        progress_bar.progress(i)
    # 完成后移除进度条
    progress_bar.empty()

# 检查文件是否都上传了
if not pm_file or not excel_file:
    if not pm_file:
        st.warning("⚠️ Please upload the .pm file to continue.")
    if not excel_file:
        st.warning("⚠️ Please upload the Excel file to continue.")
else:
    # 显示传感器配置信息
    st.markdown("<h3 class='green-text'>SYSC Info</h3>", unsafe_allow_html=True)
    pm_content = read_pm_file(pm_file)
    sensors_configured = extract_configured_sensors(pm_content)
    st.write("Configured sensors:", sensors_configured)

    # 处理 Excel 文件
    st.markdown("<h3 class='green-text'>Result</h3>", unsafe_allow_html=True)
    sheet_name = st.text_input("Enter Excel sheet name", "Settings_SensorInfo")
    try:
        df = read_excel_file(excel_file, sheet_name)
        creisrelevant_sensors = extract_creisrelevant_sensors(df)
        pm_sensors_dict = {sensor[0]: sensor[2] for sensor in sensors_configured}

        for sensor in creisrelevant_sensors:
            sensor_name = sensor['SensorName']
            creisrelevant = sensor['CREISrelevant']
            base_sensor_name = re.sub(r'X|Y$', '', sensor_name.replace('_', ''))
            configured = pm_sensors_dict.get(base_sensor_name, None)

            if configured is None:
                st.markdown(f"<span class='blue-text'>Sensor: {sensor_name}, CREISrelevant: {creisrelevant}</span>", unsafe_allow_html=True)
            elif (creisrelevant and configured.lower() != 'true') or (not creisrelevant and configured.lower() != 'false'):
                st.markdown(f"<span class='red-text'>Sensor: {sensor_name}, CREISrelevant: {creisrelevant}</span>", unsafe_allow_html=True)
            else:
                st.write(f"Sensor: {sensor_name}, CREISrelevant: {creisrelevant}")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")

# 添加页脚
st.markdown(
    """
    <hr style="border: 1px solid #4CAF50;">
    <footer style="text-align:center;">
        <p style="font-size:0.9rem;">© 2024 Bosch Sensor Verification Tool V1 by Qi Qiuchen & Li Mutong</p>
    </footer>
    """,
    unsafe_allow_html=True,
)
