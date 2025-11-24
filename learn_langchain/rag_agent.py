import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGEngine, PGVectorStore

# from langchain_openai import ChatOpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set")

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# print(llm.invoke("こんにちはお元気ですか？"))

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
connection_string = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
engine = PGEngine.from_connection_string(connection_string)

# テーブルが存在しない場合は明示的に作成
# text-embedding-3-smallのベクトルサイズは1536
# 初回のみ実行（2回目以降はコメントアウト可）
# engine.init_vectorstore_table(table_name="docs", vector_size=1536)

vector_store = PGVectorStore.create_sync(
    engine=engine, table_name="docs", embedding_service=embeddings
)
