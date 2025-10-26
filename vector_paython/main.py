from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
  RecursiveCharacterTextSplitter,
  Language
)
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from .text_load_split_and_embed import main as text_load_split_and_embed

load_dotenv()

text  = """
# EC2 (Amazon Linux 2023) から CloudWatch にアクセスログを送る手頛今残"": **EC2 のアクセスログを CloudWatch に送信する**
目的: **EC2 のアクセスログを CloudWatch に送信する**
,2025-9-3-ec2-access-logs-to-cloudwatch.md")
# ログ送信権限を付与（IAM ロー角を SSH 接続」- 作成した `.pem` キーを用いて接続
"""

md_splitter = RecursiveCharacterTextSplitter.from_language(
  language=Language.MARKDOWN, chunk_size=60, chunk_overlap=0
  )

# @see: https://docs.langchain.com/
def main():
    # textを読み込んで出力
    # md_docs = md_splitter.split_text(text)
    # print(md_docs)

    # mdファイルを読み込んで出力その1
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # print(script_dir)
    # file_path = os.path.join(script_dir, "2025-9-3-ec2-access-logs-to-cloudwatch.md")
    # loader = TextLoader(file_path)
    # chunks = md_splitter.split_documents(docs)
    # print(chunks)

    # mdファイルを読み込んで出力その2
    # loader = TextLoader("./vector_paython/2025-9-3-ec2-access-logs-to-cloudwatch.md")
    # docs = loader.load()
    # chunks = md_splitter.split_documents(docs)
    # print(chunks)

    # md_doc(list[Document])を作成
    # loader = TextLoader("./vector_paython/2025-9-3-ec2-access-logs-to-cloudwatch.md")
    # docs = loader.load()
    # docs_string = [doc.page_content for doc in docs]
    # md_doc = md_splitter.create_documents(docs_string, metadatas=[{"source": "2025-9-3-ec2-access-logs-to-cloudwatch.md"}])
    # print(md_doc)

    # 複数のdocumentを埋め込む
    # log: [[-0.0016021728515625, 0.00030517578125, 0.00030517578125, ...], [-0.0016021728515625, 0.00030517578125, 0.00030517578125, ...], [-0.0016021728515625, 0.00030517578125, 0.00030517578125, ...]]
    # model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
    # embedding = model.embed_documents(["こんにちは。", "こんにちは、今日はいい天気ですね。", "ですね。明日もいい天気になるみたいですよ。"])
    # print(embedding)

    text_load_split_and_embed()

if __name__ == "__main__":
    main()