from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
  RecursiveCharacterTextSplitter,
  Language
)
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# MDファイルを読み込んで、ドキュメントを分割し、埋め込む処理
def main():
    # MDファイルを読み込む
    loader = TextLoader("./vector_paython/2025-9-3-ec2-access-logs-to-cloudwatch.md")
    doc = loader.load()

    # ドキュメントを分割
    md_splitter = RecursiveCharacterTextSplitter.from_language(
      language=Language.MARKDOWN, chunk_size=200, chunk_overlap=20
    )
    chunks = md_splitter.split_documents(doc)

    page_contents = [chunk.page_content for chunk in chunks]

    ## 埋め込む
    # model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
    embed_contents = model.embed_documents(page_contents)
    print(embed_contents)
    

if __name__ == "__main__":
    main()