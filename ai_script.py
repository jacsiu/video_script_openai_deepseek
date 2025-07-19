from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.utilities import WikipediaAPIWrapper
import wikipedia
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_script(subject, video_length, creativity, api_key):
    # 设置重试机制和超时
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    # 配置wikipedia库
    wikipedia.set_lang("zh")
    session.timeout = 10 # 设置超时时间为10秒
    wikipedia.__session = session  # 使用配置好的session

    title_template = ChatPromptTemplate.from_messages(
        [
            ("human", "请为'{subject}'这个主题的视频想一个吸引人的标题")
        ]
    )

    script_template = ChatPromptTemplate.from_messages(
        [
            ("human",
             """你是一位短视频频道的博主。根据以下标题和相关信息，为短视频频道写一个视频脚本。
             视频标题：{title}，视频时长：{duration}分钟，生成的脚本的长度尽量遵循视频时长的要求。
             要求开头抓住眼球，中间提供干货内容，结尾有惊喜，脚本格式也请按照【开头、中间，结尾】分隔。
             整体内容的表达方式要尽量轻松有趣，吸引年轻人。
             脚本内容可以结合以下维基百科搜索出的信息，但仅作为参考，只结合相关的即可，对不相关的进行忽略：
             ```{wikipedia_search}```
            """)
        ]
    )

    model = ChatOpenAI(
        openai_api_key=api_key,
        temperature=creativity,
        model="deepseek/deepseek-r1:free",
        base_url="https://openrouter.ai/api/v1",
        max_retries=3,  # 设置模型调用的最大重试次数
        request_timeout=60  # 设置请求超时时间为60秒
    )

    title_chain = title_template | model
    script_chain = script_template | model

    try:
        logger.info(f"生成标题: {subject}")
        title = title_chain.invoke({"subject": subject}).content
        logger.info(f"生成的标题: {title}")

        # 获取维基百科搜索结果，添加重试逻辑
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                logger.info(f"尝试获取维基百科信息: {subject} (尝试 {attempt + 1}/{max_attempts})")
                search = WikipediaAPIWrapper(lang="zh",)
                search_result = search.run(subject)
                logger.info("成功获取维基百科信息")
                break
            except Exception as e:
                if attempt == max_attempts - 1:
                    logger.error(f"获取维基百科信息失败: {str(e)}")
                    # 如果多次尝试都失败，提供一个默认信息
                    search_result = f"关于{subject}的信息无法从维基百科获取，请手动补充相关内容。"
                else:
                    logger.warning(f"尝试 {attempt + 1} 失败，等待 {2 ** attempt} 秒后重试: {str(e)}")
                    time.sleep(2 ** attempt)  # 指数退避策略

        logger.info("生成视频脚本...")
        script = script_chain.invoke(
            {"title": title, "duration": video_length, "wikipedia_search": search_result}).content
        logger.info("视频脚本生成完成")

        return search_result, title, script

    except Exception as e:
        logger.error(f"生成脚本时发生错误: {str(e)}")
        # 返回错误信息而不是让程序崩溃
        return f"错误: {str(e)}", "", ""


# if __name__ == "__main__":
#     try:
#         result = generate_script(
#             "sora模型",
#             1,
#             0.8,
#             "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"
#         )
#         print("搜索结果:", result[0])
#         print("标题:", result[1])
#         print("脚本:", result[2])
#     except KeyboardInterrupt:
#         print("\n程序被用户中断")