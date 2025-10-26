from langchain_core.documents.base import Document


import os
import uuid
from langchain_community.document_loaders import TextLoader
# 削除された模様
# from langchain_core.storage import InMemoryStore
from langchain_text_splitters import (
  RecursiveCharacterTextSplitter,
  Language
)
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from dotenv import load_dotenv

load_dotenv()

connection_string = 'postgresql+psycopg://langchain:langchain@localhost:6024/langchain'

collection_name = 'summaries_documents'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

loader = TextLoader("./vector_paython/2025-9-3-ec2-access-logs-to-cloudwatch.md")
docs = loader.load()
print("読み込んだドキュメントの長さ:", len(docs[0].page_content))

md_splitter = RecursiveCharacterTextSplitter.from_language(
  language=Language.MARKDOWN, chunk_size=200, chunk_overlap=20
)
chunks = md_splitter.split_documents(docs)

prompt_text = """
以下のドキュメントを要約してください。
`XXXの概要`を一番最初に書いてください。
XXXには、ドキュメントのタイトルを書いてください。

{doc}
"""

prompt = ChatPromptTemplate.from_template(prompt_text)
GPT_o4_mini_model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
summarize_chain = {
  "doc": lambda x: x.page_content } | prompt | GPT_o4_mini_model | StrOutputParser()

engine = PGEngine.from_connection_string(connection_string)

# engine.init_vectorstore_table(table_name="docs", vector_size=1536)  # JSONB スキーマで作られます
# engine.init_vectorstore_table(table_name="summaries_documents", vector_size=1536)  # JSONB スキーマで作られます
vectorstore = PGVectorStore.create_sync(engine=engine, table_name="docs", embedding_service=OpenAIEmbeddings())
vectorstore_summaries = PGVectorStore.create_sync(engine=engine, table_name="summaries_documents", embedding_service=OpenAIEmbeddings())

def main():
    # ベクトルストアを作成
    chunked_docs = [
        # enumerateを使わない場合、forループで直接リストの要素を取得できますが、要素（s）しか得られず、インデックス（i）は得られません。
        # 例えば: for s in chunks: とするとsだけが手に入ります。
        # インデックス（番号）も一緒に使いたい場合は、enumerateを使って「for i, s in enumerate(chunks)」のように書きます。
        # これにより、iに各要素の番号（0, 1, 2,...）、sに各要素が入ります。
        Document(page_content=s.page_content, metadata={"index": i})
        for i, s in enumerate[Document](chunks)
    ]
    vectorstore.add_documents(chunked_docs)
    

    # ベクトルストアに要約を追加
    summaries = summarize_chain.batch(docs, {"max": 5})
    print("summaries--------------------------------")
    print(summaries)
    summary_docs = [
        Document(page_content=s, metadata={"index": i})
        for i, s in enumerate(summaries)
    ]
    vectorstore_summaries.add_documents(summary_docs)
    
    # 類似度検索
    # sub_docs = vectorstore_summaries.similarity_search("EC2 のアクセスログを CloudWatch に送信する", k=3)
    # print("sub_docs--------------------------------")
    # print(sub_docs)

if __name__ == "__main__":
    main()