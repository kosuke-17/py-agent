"""
Semantic SearchエンジンをLangcHainで構築する.
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

documents = [
    Document(
        page_content="犬は動物です。散歩が大好きです。",
        metadata={
            "source": "mammal-pets-doc"
        },  # メタデータは中身の内容についての補足情報。大きなドキュメントをチャンクで分割した際に、どのドキュメントからのものかを示すために使用される。
    ),
    Document(
        page_content="ねこは動物です。家にいるときは、ずっと寝ています。",
        metadata={"source": "mammal-pets-doc"},
    ),
]

# ドキュメントを出力
# documents--------------------------------
# [
#   Document(metadata={'source': 'mammal-pets-doc'}, page_content='犬は動物です。散歩が大好きです。'),
#   Document(metadata={'source': 'mammal-pets-doc'}, page_content='ねこは動物です。家にいるときは、ずっと寝ています。')
# ]
# print("documents--------------------------------")
# print(documents)

# ドキュメントを読み込む
# @see: https://docs.langchain.com/oss/python/langchain/knowledge-base#loading-documents
file_path = "./learn_langchain/nke-10k-2023.pdf"

loader = PyPDFLoader(file_path)
docs = loader.load()
# print("docs--------------------------------")
# print(docs)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=10, chunk_overlap=3, add_start_index=True
)
all_splits = text_splitter.split_documents(documents)
# print("all_splits--------------------------------")
# for split in all_splits:
#     print("--------------------------------")
#     print(split)
#     print("--------------------------------")
# print(len(all_splits))
