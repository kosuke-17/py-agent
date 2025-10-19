from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv
load_dotenv()

# モデルインスタンス作成
# temperature=0 は確率を0に固定して、常に同じ回答を返す
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

# プロンプトのテンプレート文章を定義
template = """
次の文章に誤字がないかしらべて。誤字があれば訂正してください。
{sentences_before_check}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは、優秀な校正者です。"),
    ("user", template),
])

# チャットメッセージを文章に変換するための出力解析インスタンスを作成
output_parser = StrOutputParser()

chain = prompt | llm | output_parser

def check_typos(sentences_before_check: str) -> str:
    result = chain.invoke({"sentences_before_check": sentences_before_check})
    return result
