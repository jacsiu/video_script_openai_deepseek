import streamlit as st
from streamlit import expander

from ai_script import generate_script

st.title("🚥视频脚本生成器")

with st.sidebar:
   openai_api = st.text_input("请输入OpenAI API密钥",type="password")
   st.markdown("[获取OpenAI API密钥](https://platform.openai.com/account/api-keys)")
subject = st.text_input("💡 请输入视频主题")
video_length = st.number_input("请输入视频的大致时长（单位：分钟）",min_value=0.1,step=0.1)
creativity = st.slider("⭐ 请输入视频脚本的创造力（数字越小说明更严谨，反之更多样）",min_value=0.0,max_value=1.0,
          value=0.5,step=0.1)
submit = st.button("生成脚本")

if submit and not openai_api:
    st.info("请输入你的OpenAI密钥")
    st.stop()
if submit and not subject:
    st.info("请输入视频主题")
    st.stop()
if submit and not video_length >= 0.1:
    st.info("视频长度需要大于等于0.1分钟！")
    st.stop()
if submit:
    with st.spinner(("AI正在思考中，请稍等...")):
        search_result, title, script = generate_script(subject,video_length,creativity,openai_api)
    st.success("视频脚本已生成！")
    st.subheader("🔥 标题：")
    st.write(title)
    st.subheader("🖊️ 视频脚本：")
    st.write(script)
    with expander("维基百科搜索结果 👀"):
        st.write(search_result)

