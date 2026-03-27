import streamlit as st
import requests
import os

# -------------------------- 配置 --------------------------
# 从环境变量读取 API Key，更安全
ZAI_API_KEY = os.getenv("ZAI_API_KEY", "")

# 如果环境变量未设置，提供备用方式
if not ZAI_API_KEY:
    st.error("⚠️ 请设置环境变量 ZAI_API_KEY")

# Z.AI 调用地址（官方标准接口）
ZAI_URL = "https://api.z.ai/v1/chat/completions"

# 页面配置
st.set_page_config(page_title="健身AI教练", page_icon="💪", layout="centered")

# 标题
st.title("💪 健身行业AI指导助手")
st.subheader("您的专业健身私教")

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是你的专业AI健身教练🏋️\n告诉我你的目标（增肌/减脂/塑形）、身体情况，我为你定制计划！"}
    ]

# 行业AI核心：健身教练系统提示词（作业加分点）
SYSTEM_PROMPT = """
你是一位专业持证的健身私教，属于【健身健康垂直行业AI】。
你的职责：
1. 根据用户情况制定个性化训练计划
2. 讲解动作标准、发力方式、避免受伤
3. 提供饮食营养、减脂增肌饮食方案
4. 回答健身相关问题
5. 提醒运动安全，不提供危险动作

回答风格：专业、简洁、可执行、有耐心。
绝不回答健身以外的内容，严格保持行业AI定位。
"""

# -------------------------- 展示对话 --------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------- 用户输入 --------------------------
user_input = st.chat_input("输入你的健身问题：")

if user_input:
    # 加入对话历史
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 调用 Z.AI
    with st.chat_message("assistant"):
        with st.spinner("健身AI思考中..."):
            try:
                # 构造请求体
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + st.session_state.messages

                payload = {
                    "model": "zai-v1",  # 用Z.AI默认模型
                    "messages": messages,
                    "temperature": 0.7
                }

                headers = {
                    "Authorization": f"Bearer {ZAI_API_KEY}",
                    "Content-Type": "application/json"
                }

                # 发送请求
                response = requests.post(ZAI_URL, json=payload, headers=headers, timeout=30)

                # 检查响应状态
                response.raise_for_status()

                result = response.json()

                # 验证响应结构
                if "choices" in result and len(result["choices"]) > 0:
                    ai_reply = result["choices"][0]["message"]["content"]
                else:
                    ai_reply = "抱歉，AI返回的格式有误，请稍后重试。"

            except requests.exceptions.Timeout:
                ai_reply = "请求超时，请检查网络连接后重试。"
            except requests.exceptions.ConnectionError:
                ai_reply = "网络连接失败，请检查您的网络设置。"
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    ai_reply = "API密钥无效，请检查配置。"
                elif response.status_code == 429:
                    ai_reply = "请求过于频繁，请稍后再试。"
                else:
                    ai_reply = f"API请求失败 (HTTP {response.status_code}): {str(e)}"
            except KeyError:
                ai_reply = "AI返回的数据格式异常，请稍后重试。"
            except Exception as e:
                ai_reply = f"发生未知错误: {str(e)}"

            # 显示回答
            st.markdown(ai_reply)

    # 保存AI回复
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
