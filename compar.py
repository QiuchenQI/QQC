import re
import pandas as pd
import streamlit as st
import time
import io
import seaborn as sns
import matplotlib.pyplot as plt

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
        color: #4CAF50;
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
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .button-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }
    .stDataFrame {
        background-color: #f9f9f9;
        border-radius: 8px;
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

def create_verification_report(matching_sensors, mismatched_sensors, extra_sensors):
    # 创建DataFrame用于导出
    data = {
        "Sensor Name": [],
        "CREISrelevant": [],
        "Status": []
    }

    for sensor in matching_sensors:
        data["Sensor Name"].append(sensor[0])
        data["CREISrelevant"].append(sensor[1])
        data["Status"].append("Matching")

    for sensor in mismatched_sensors:
        data["Sensor Name"].append(sensor[0])
        data["CREISrelevant"].append(sensor[1])
        data["Status"].append("Mismatched")

    for sensor in extra_sensors:
        data["Sensor Name"].append(sensor[0])
        data["CREISrelevant"].append(sensor[1])
        data["Status"].append("Extra")

    # 将数据转换为DataFrame
    df_report = pd.DataFrame(data)
    return df_report

# 标题和说明
st.markdown('<div class="title">Sensor Info Verification</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Extra sensors will be marked in blue, Wrong configuration in red</div>', unsafe_allow_html=True)

# 上传文件部分
col1, col2 = st.columns(2)

with col1:
    pm_file = st.file_uploader("Upload .pm File", type=["pm"])
with col2:
    excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])

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

    # 展开/收起的显示功能
    with st.expander("Configured Sensors", expanded=True):
        st.write("Configured sensors:", sensors_configured)

    # 处理 Excel 文件
    st.markdown("<h3 class='green-text'>Result</h3>", unsafe_allow_html=True)
    sheet_name = st.text_input("Enter Excel sheet name", "Settings_SensorInfo")
    try:
        df = read_excel_file(excel_file, sheet_name)
        creisrelevant_sensors = extract_creisrelevant_sensors(df)
        pm_sensors_dict = {sensor[0]: sensor[2] for sensor in sensors_configured}

        # 比较视图展示
        matching_sensors = []
        mismatched_sensors = []
        extra_sensors = []

        for sensor in creisrelevant_sensors:
            sensor_name = sensor['SensorName']
            creisrelevant = sensor['CREISrelevant']
            base_sensor_name = re.sub(r'X|Y$', '', sensor_name.replace('_', ''))
            configured = pm_sensors_dict.get(base_sensor_name, None)

            if configured is None:
                extra_sensors.append((sensor_name, creisrelevant))
            elif (creisrelevant and configured.lower() != 'true') or (not creisrelevant and configured.lower() != 'false'):
                mismatched_sensors.append((sensor_name, creisrelevant))
            else:
                matching_sensors.append((sensor_name, creisrelevant))

        # 展示匹配的传感器
        with st.expander("Matching Sensors", expanded=True):
            if matching_sensors:
                for sensor in matching_sensors:
                    st.write(f"Sensor: {sensor[0]}, CREISrelevant: {sensor[1]}")
            else:
                st.write("No matching sensors found.")

        # 展示错误配置的传感器
        with st.expander("Mismatched Sensors", expanded=True):
            if mismatched_sensors:
                for sensor in mismatched_sensors:
                    st.markdown(f"<span class='red-text'>Sensor: {sensor[0]}, CREISrelevant: {sensor[1]}</span>", unsafe_allow_html=True)
            else:
                st.write("No mismatched sensors found.")

        # 展示额外的传感器
        with st.expander("Extra Sensors", expanded=True):
            if extra_sensors:
                for sensor in extra_sensors:
                    st.markdown(f"<span class='blue-text'>Sensor: {sensor[0]}, CREISrelevant: {sensor[1]}</span>", unsafe_allow_html=True)
            else:
                st.write("No extra sensors found.")

        # 导出结果
        st.markdown("<h3 class='green-text'>Picture of result</h3>", unsafe_allow_html=True)
        df_report = create_verification_report(matching_sensors, mismatched_sensors, extra_sensors)

        # 数据可视化：展示配置是否正确的传感器数量，错误配置的比例等
        sensor_status = {'Matching': len(matching_sensors), 'Mismatched': len(mismatched_sensors), 'Extra': len(extra_sensors)}
        status_df = pd.DataFrame(list(sensor_status.items()), columns=['Status', 'Count'])

        # 使用seaborn绘制条形图
        plt.figure(figsize=(8, 6))
        sns.barplot(x='Status', y='Count', data=status_df, palette=["#CC2B52", "#FFB26F", "#7AB2D3"])

        # 为每个柱子添加数字标注
        for index, row in status_df.iterrows():
            plt.text(row.name, row['Count'], round(row['Count'], 2), color='black', ha="center", va="bottom", fontweight='bold')

        plt.title("Picture Version of Result")
        plt.ylabel("Number of Sensors")
        plt.xlabel("Status")
        st.pyplot(plt)

        # 展示表格
        st.markdown("<h3 class='green-text'>Form Version of Result</h3>", unsafe_allow_html=True)
        st.dataframe(df_report, use_container_width=True)

        # 提供CSV和Excel下载按钮
        csv = df_report.to_csv(index=False)

        # 创建Excel文件的BytesIO对象（使用openpyxl）
        excel_io = io.BytesIO()
        with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
            df_report.to_excel(writer, index=False, sheet_name="Report")
        excel_io.seek(0)

        st.markdown("<h3 class='green-text'>Download Result</h3>", unsafe_allow_html=True)
        # 下载按钮
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="verification_report.csv",
                mime="text/csv",
            )

        with col2:
            st.download_button(
                label="Download Excel",
                data=excel_io,
                file_name="verification_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    except Exception as e:
        st.error(f"Error reading the Excel file or extracting data: {e}")

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
