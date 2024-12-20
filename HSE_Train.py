import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 设置页面布局为宽屏模式
st.set_page_config(layout="wide", page_title="OSS-ENG Lab HSE Training", page_icon=":books:")

# 使用 HTML 和 CSS 美化页面
page_style = '''
<style>
body {
    font-family: 'Calibri', sans-serif;
    background-color: #f0f2f6;
}
h1 {
    font-size: 48px;
    color: #000000;
}
h2 {
    font-size: 14px;
    color: #000000;
}
h3 {
    font-size: 20px;
    color: #000000;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;
}
.stButton>button:hover {
    background-color: #45a049;
}
</style>
'''

st.markdown(page_style, unsafe_allow_html=True)

# 页面标题
st.markdown('<h1>OSS-ENG Lab HSE Training</h1>', unsafe_allow_html=True)
st.markdown('<h2>Any questions please contact with QI Qiuchen(VM-OSS/ESS2-CN)</h2>', unsafe_allow_html=True)

# 页面选择
page = st.selectbox("Admin/Users", ["Users", "Admin"])

# 全局变量存储用户得分情况
if 'scores' not in st.session_state:
    st.session_state.scores = []

# Excel 文件路径
excel_file = 'C:/HSE_Training/Record.xlsx'
temp_excel_file = 'C:/HSE_Training/Temp_Record.xlsx'
status_file = 'C:/HSE_Training/VN-OSS-ENG Lab HSE Level 3 trainning status.xlsx'
training_material_path = 'C:/HSE_Training/VM_OSS_ENG_LAB_EHS_TRAINING(L3).pptx'

if page == "Users":
    # 读取用户信息
    if os.path.exists(status_file):
        user_data = pd.read_excel(status_file)
        names = user_data['Name'].tolist()
        departments = user_data['Department'].tolist()
        user_options = [""] + [f"{name} ({department})" for name, department in zip(names, departments)]
    else:
        st.error("No configuration file found.")
        user_options = [""]

    # 用户姓名登记
    st.header("Login in")
    if 'selected_user' not in st.session_state:
        st.session_state.selected_user = None

    if st.session_state.selected_user is None:
        selected_user = st.selectbox("Please select...", user_options, index=0)
        if st.button("OK"):
            st.session_state.selected_user = selected_user
    else:
        selected_user = st.session_state.selected_user
        user_name, user_department = selected_user.split(" (")
        user_department = user_department.rstrip(")")

        # 显示已选择的用户信息
        st.write(f"Selected User: {user_name} ({user_department})")

        # 下载培训材料
        st.header("HSE Training material")
        if os.path.exists(training_material_path):
            with open(training_material_path, "rb") as f:
                st.download_button(
                    label="Download HSE L3 Training Material",
                    data=f,
                    file_name="VM_OSS_ENG_LAB_EHS_TRAINING(L3).pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
        else:
            st.error("Training material not found.")

        # 答题功能
        st.header("Exam")

        # 问题及选项
        questions = [
            {
                "type": "fill_in_the_blank",
                "question": "Emergency Call(紧急电话) example xxxx-xxxx",
                "answer": "6767-6119"
            },
            {
                "type": "fill_in_the_blank",
                "question": "First aid call(急救电话) example xxxx-xxxx",
                "answer": "6767-6120"
            },
            {
                "type": "multiple_choice",
                "question": "手枪钻的推荐使用扭矩是多少?What's the Drill machine's reference torque?",
                "options": ["3~4", "5~6", "7~8", "9~10"],
                "answer": "5~6"
            },
            {
                "type": "multiple_choice",
                "question": "实验室ERT成员有哪些?Who is LAB ERT member?",
                "options": ["Li Yichang", "Jiao Haibin", "Tan Jiawei", "Wei Wei"],
                "answer": "Jiao Haibin"
            },
            {
                "type": "multiple_choice",
                "question": "Near miss是否可以通过eFMS上报?Whether Near miss can report through eFMS?",
                "options": ["Yes", "No"],
                "answer": "Yes"
            },
            {
                "type": "multiple_choice",
                "question": "下图是否存在电气安全风险?Whether the below picture has the electrical risk?",
                "options": ["Yes", "No"],
                "answer": "Yes",
                "image": "C:/HSE_Training/1.jpg"  # 添加图片路径
            },
            {
                "type": "subjective",
                "question": "列出急救事故和伤害事故的区别List the distinguish between First Aid and Injury",
                "keywords": ["a", "b", "c", "d", "e"]
            },
            {
                "type": "subjective",
                "question": "实验室有哪些危险源(列出至少3项)What are the lab hazards (List at least 3 items)",
                "keywords": ["a", "b", "c", "d", "e"]
            }
        ]

        # 用户提交答案
        user_answers = {}
        for i, q in enumerate(questions):
            st.subheader(f"Questions {i + 1}: {q['question']}")
            if "image" in q:
                st.image(q["image"], caption="Question Image", use_container_width=True, width=50)  # 设置图片宽度
            if q["type"] == "multiple_choice":
                user_answers[q["question"]] = st.radio(
                    f"Please select your answer：",
                    q["options"],
                    key=f"q{i}",
                    index=None  # 初始状态不选中任何项
                )
            elif q["type"] == "fill_in_the_blank":
                user_answers[q["question"]] = st.text_input(
                    f"Please fill in your answer：",
                    key=f"q{i}"
                )
            elif q["type"] == "subjective":
                user_answers[q["question"]] = st.text_area(
                    f"Please write your answer：",
                    key=f"q{i}"
                )

        # 提交按钮
        if st.button("OK"):
            score = 0
            for q in questions:
                if q["type"] == "multiple_choice" or q["type"] == "fill_in_the_blank":
                    if user_answers[q["question"]] == q["answer"]:
                        score += 1
                elif q["type"] == "subjective":
                    if "keywords" in q:
                        user_answer = user_answers[q["question"]].lower()
                        keywords = q["keywords"]
                        match_count = sum(1 for keyword in keywords if keyword in user_answer)
                        if match_count >= len(keywords) / 2:
                            score += 1
            
            st.subheader("测试结果")
            total_questions = len(questions)
            passing_score = total_questions * 0.8
            st.write(f"Your scores：{score}/{total_questions}")
            
            if score >= passing_score:
                st.success("PASS")
                valid_days = 365
            else:
                st.warning("FAIL")
                valid_days = 0

            # 读取现有记录
            if os.path.exists(excel_file):
                df = pd.read_excel(excel_file)
            else:
                df = pd.DataFrame(columns=["name", "department", "score", "time", "valid_days", "status"])

            # 更新用户记录
            if user_name in df["name"].values:
                current_valid_days = df.loc[df["name"] == user_name, "valid_days"].values[0]
                df.loc[df["name"] == user_name, "score"] = score
                df.loc[df["name"] == user_name, "time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[df["name"] == user_name, "valid_days"] = min(365, current_valid_days + valid_days)
            else:
                new_record = pd.DataFrame([{"name": user_name, "department": user_department, "score": score, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "valid_days": valid_days, "status": "Normal" if valid_days >= 30 else "Warning"}])
                df = pd.concat([df, new_record], ignore_index=True)

            # 更新状态
            df["valid_days"] = df.apply(lambda row: max(0, min(365, row["valid_days"] - (datetime.now() - pd.to_datetime(row["time"])).days)), axis=1)
            df["status"] = df["valid_days"].apply(lambda x: "Normal" if x >= 30 else "Warning")

            # 保存到临时 Excel 文件
            df.to_excel(temp_excel_file, index=False)

            # 替换原始 Excel 文件
            os.replace(temp_excel_file, excel_file)

elif page == "Admin":
    st.header("Login in")
    password = st.text_input("Please enter with your password", type="password")
    
    if password == "123456":
        st.success("Login in successfully")
        st.header("Training record")
        # 显示答题汇总情况
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            
            # 设置行颜色
            def color_rows(row):
                return ['background-color: green' if row['status'] == 'Normal' else 'background-color: red'] * len(row)

            styled_df = df.style.apply(color_rows, axis=1)
            st.dataframe(styled_df, width=1200)  # 调宽表格

            # 显示所有 status 为 Warning 的用户信息
            warning_users = df[df['status'] == 'Warning']
            st.subheader("Users with Warning Status")
            st.dataframe(warning_users, width=1200)  # 调宽表格

            # 获取用户的 Email 地址
            if os.path.exists(status_file):
                user_data = pd.read_excel(status_file)
                warning_emails = user_data[user_data['Name'].isin(warning_users['name'])]['Email'].dropna().tolist()
                if warning_emails:
                    email_addresses = ', '.join(warning_emails)
                    st.text_area("Email Addresses", email_addresses, key="email_area")
                else:
                    st.error("No email addresses found for users with Warning status.")
            else:
                st.error("User information file not found.")
        else:
            st.write("No records yet.")
    elif password:
        st.error("Please try again")
