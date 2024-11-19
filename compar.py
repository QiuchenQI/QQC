import re
import pandas as pd
import streamlit as st

def read_pm_file(pm_file):
    return pm_file.read().decode('utf-8')

def extract_configured_sensors(pm_content):
    # 定义正则表达式模式，匹配传感器名称和configured属性
    pattern = re.compile(r'(\w+)\s*=>\s*{\s*"(\w+)"\s*=>\s*{configured\s*=>\s*"(\w+)"', re.IGNORECASE)
    matches = pattern.findall(pm_content)
    
    # 提取传感器名称和configured属性
    sensors_configured = [(match[0], match[1], match[2]) for match in matches]
    return sensors_configured

def read_excel_file(excel_file, sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    return df

def extract_creisrelevant_sensors(df):
    # 提取CREISrelevant属性的传感器名称
    creisrelevant_sensors = df[['SensorName', 'CREISrelevant']].to_dict('records')
    return creisrelevant_sensors

# Streamlit UI
st.title("Sensorinfo verification")
st.title("extra sensors will be marked in blue, Wrong configuration will be marked in red")

# 上传 .pm 文件
pm_file = st.file_uploader("上传 .pm 文件", type=["pm"])
# 上传 Excel 文件
excel_file = st.file_uploader("上传 Excel 文件", type=["xlsx"])

st.title("Below is Syc info")
if pm_file:
    # 读取 .pm 文件内容
    pm_content = read_pm_file(pm_file)
    sensors_configured = extract_configured_sensors(pm_content)
    st.write("传感器的配置信息 (传感器, 通道, Configured):", sensors_configured)
    for sensor in sensors_configured:
        st.write(f"传感器: {sensor[0]}, 通道: {sensor[1]}, Configured: {sensor[2]}")

st.title("Below is result")
if excel_file:
    # 读取 Excel 文件内容
    sheet_name = st.text_input("请输入要读取的 Excel 表格名称", "Settings_SensorInfo")
    try:
        df = read_excel_file(excel_file, sheet_name)
        creisrelevant_sensors = extract_creisrelevant_sensors(df)
        
        # 创建一个字典来存储 .pm 文件中的传感器信息
        pm_sensors_dict = {sensor[0]: sensor[2] for sensor in sensors_configured}
        
        for sensor in creisrelevant_sensors:
            sensor_name = sensor['SensorName']
            creisrelevant = sensor['CREISrelevant']
            
            # 处理传感器名称，去掉下划线并处理UFSDX, UFSDY等情况
            base_sensor_name = re.sub(r'X|Y$', '', sensor_name.replace('_', ''))
            configured = pm_sensors_dict.get(base_sensor_name, None)
            
            if configured is None:
                st.markdown(f"<span style='color: Blue;'>传感器: {sensor_name}, CREISrelevant: {creisrelevant}</span>", unsafe_allow_html=True)
            elif (creisrelevant and configured.lower() != 'true') or (not creisrelevant and configured.lower() != 'false'):
                st.markdown(f"<span style='color: red;'>传感器: {sensor_name}, CREISrelevant: {creisrelevant}</span>", unsafe_allow_html=True)
            else:
                st.write(f"传感器: {sensor_name}, CREISrelevant: {creisrelevant}")
    except Exception as e:
        st.error(f"读取 Excel 文件时出错: {e}")