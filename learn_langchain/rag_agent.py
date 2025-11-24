"""
RAGエージェントをLangChainで構築する.
https://docs.langchain.com/oss/python/langchain/rag#loading-documents
"""

import os

# import bs4  # フィルタリングが必要な場合はコメントアウトを解除
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

# tamusite.comはNext.jsのSPAで、コンテンツがJavaScriptで動的に生成される
# WebBaseLoaderは静的HTMLのみを取得するため、JavaScriptで生成されるコンテンツは取得できない
#
# 解決策1: 個別の記事ページのURLを指定（SSRされている可能性がある）
# 解決策2: bs_kwargsをコメントアウトして全HTMLを取得し、後でフィルタリング
# 解決策3: PlaywrightなどでJavaScriptを実行してレンダリング

# オプション1: フィルタリングなし（全HTMLを取得）
loader = WebBaseLoader(
    web_paths=("https://tamusite.com",),
)

# オプション2: セマンティックなHTMLタグでフィルタリング（記事ページの場合）
# bs4_strainer = bs4.SoupStrainer(["main", "article", "header"])
# loader = WebBaseLoader(
#     web_paths=(
#         "https://tamusite.com/blogs/aws/2025-9-3-ec2-access-logs-to-cloudwatch.md",
#     ),
#     bs_kwargs={"parse_only": bs4_strainer},
# )

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=10,
    chunk_overlap=3,
    add_start_index=True,
)
all_splits = text_splitter.split_documents(docs)

print(f"{len(all_splits)}のサブドキュメントに分割されました。")

document_ids = vector_store.add_documents(documents=all_splits)
print(f"ドキュメントが追加されました: {document_ids}")
