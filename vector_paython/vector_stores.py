import uuid
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
  RecursiveCharacterTextSplitter,
  Language
)
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document

load_dotenv()

md_splitter = RecursiveCharacterTextSplitter.from_language(
  language=Language.MARKDOWN, chunk_size=200, chunk_overlap=20
)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

# db用のコンテナ起動の例
# docker run --name pgvector-db -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -d pgvector/pgvector:pg16
def main():
    # ドキュメントを読み込んでチャンクに分割
    loader = TextLoader("./vector_paython/2025-9-3-ec2-access-logs-to-cloudwatch.md")
    docs = loader.load()
    chunked_documents = md_splitter.split_documents(docs)

    # チャンクごとに埋め込みを生成して、ベクトルストアに保存する
    # psycopgはPython からPostgreSQLに接続するためのデータベース アダプター。
    connection_string = 'postgresql+psycopg://langchain:langchain@localhost:6024/langchain'
    db = PGVector.from_documents(
      # documents=chunked_documents,
      documents=[], # 空のリストを渡すと、ベクトルストアに保存されない
      embedding=model,
      connection_string=connection_string,
    )

    ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]

    db.add_documents([
      Document(
        page_content="ECRのイメージを作成する",
        metadata={
          "location":"Tokyo",
          "topic":"ECR",
        }
      ),
      Document(
        page_content="ECRにイメージをプッシュする",
        metadata={
          "location":"Tokyo",
          "topic":"ECR",
        }
      ),
      Document(
        page_content="ECRのクロスリージョンレプリケーションを設定する",
        metadata={
          "location":"Tokyo",
          "topic":"ECR",
        }
      )
    ], ids=ids)

    # k=3 は、3つの最も類似したドキュメントを返す
    results = db.similarity_search("EC2 のアクセスログを CloudWatch に送信する", k=3)
    print(results)



if __name__ == "__main__":
    main()