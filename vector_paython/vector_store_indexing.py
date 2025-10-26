import uuid
# https://python.langchain.com/api_reference/_modules/langchain_core/indexing/base.html?utm_source=chatgpt.com
from langchain_core.indexing import index
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
  RecursiveCharacterTextSplitter,
  Language
)
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_postgres import PGEngine, PGVectorStore
from langchain_core.documents import Document
from langchain_core.indexing.base import InMemoryRecordManager

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
namespace = "my_docs_namespace"
TABLE = "docs"
VECTOR_SIZE = 1536 
CONN = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

# model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

md_splitter = RecursiveCharacterTextSplitter.from_language(
  language=Language.MARKDOWN, chunk_size=200, chunk_overlap=20
)

# db用のコンテナ起動の例
# docker run --name pgvector-db -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -d pgvector/pgvector:pg16
def main():
    engine = PGEngine.from_connection_string(CONN)
    # DB作成した初回のみコメントアウトをはずして実行する
    # engine.init_vectorstore_table(table_name=TABLE, vector_size=VECTOR_SIZE)  # JSONB スキーマで作られます
    vectorstore = PGVectorStore.create_sync(engine=engine, table_name=TABLE, embedding_service=OpenAIEmbeddings())

    record_manager = InMemoryRecordManager(namespace=TABLE)
    record_manager.create_schema()

    # indexを貼ってレコード作成
    # docs = [
    #   Document(page_content="ECSを作成する", metadata={"id": str(uuid.uuid4()), "location":"Tokyo", "topic":"ECS"}),
    #   Document(page_content="ECSにデプロイする", metadata={"id": str(uuid.uuid4()), "location":"Tokyo", "topic":"ECS"})
    # ]
    # index_1 = index(
    #   docs,
    #   record_manager,
    #   vectorstore,
    #   cleanup="incremental",
    #   source_id_key="id",
    # )
    # print("index_1:", index_1)

    # index_2 = index(
    #   docs,
    #   record_manager,
    #   vectorstore,
    #   cleanup="incremental",
    #   source_id_key="id",
    # )
    # print("index_2:", index_2)

    # # ドキュメントの内容を変更して、再インデックス
    # docs[0].page_content = "ECSを削除する"
    # index_3 = index(
    #   docs,
    #   record_manager,
    #   vectorstore,
    #   cleanup="incremental",
    #   source_id_key="id",
    # )
    # print("index_3:", index_3)

    loader = TextLoader("./vector_paython/2025-9-3-ec2-access-logs-to-cloudwatch.md")
    docs = loader.load()
    splited_docs = md_splitter.split_documents(docs)
    docs = [Document(page_content=doc.page_content, metadata={"id": str(uuid.uuid4()), "location":"Tokyo", "topic":"Markdown"}) for doc in splited_docs]
    index_1 = index(
      docs,
      record_manager,
      vectorstore,
      cleanup="incremental",
      source_id_key="id",
    )
    print("index_1:", index_1)


if __name__ == "__main__":
    main()