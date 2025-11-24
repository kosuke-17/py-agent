"""
RAGエージェントをLangChainで構築する.
https://docs.langchain.com/oss/python/langchain/rag#loading-documents
"""

import os
import re
from datetime import datetime

# import bs4  # フィルタリングが必要な場合はコメントアウトを解除
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
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


def gen_document_from_chunk(
    current_chunk: str, metadata: dict, written_date: str
) -> Document:
    return Document(
        page_content=current_chunk.strip(),
        metadata={
            "source": metadata["source"],
            "written_date": written_date,
            "current_date": datetime.now(),
        },
    )


# 日付パターン（例：2025年10月11日、2024年12月31日など）で分割するカスタムスプリッター
def split_by_date_pattern(documents):
    """
    日付パターン（YYYY年MM月DD日）でドキュメントを分割する
    日付の後にタイトルがない場合はスキップする
    """
    date_pattern = r"(\d{4}年\d{1,2}月\d{1,2}日)"
    split_docs = []

    for doc in documents:
        content = doc.page_content
        # 日付パターンで分割（日付も含める）
        parts = re.split(date_pattern, content)

        current_chunk = ""
        written_date = None

        for i, part in enumerate(parts):
            if re.match(date_pattern, part):
                # 日付パターンが見つかった場合、前のチャンクを保存
                if current_chunk.strip():
                    # 日付だけ、または日付+改行+空白だけの場合はスキップ
                    chunk_without_date = re.sub(
                        date_pattern + r"\s*\n?", "", current_chunk.strip()
                    )
                    is_empty = not bool(chunk_without_date.strip())
                    if is_empty:
                        continue

                    document = gen_document_from_chunk(
                        current_chunk=current_chunk,
                        metadata=doc.metadata,
                        written_date=written_date,
                    )
                    split_docs.append(document)

                written_date = part
                current_chunk = part + "\n"
            else:
                current_chunk += part

        # 最後のチャンクを追加
        if current_chunk.strip():
            # 日付だけ、または日付+改行+空白だけの場合はスキップ
            chunk_without_date = re.sub(
                date_pattern + r"\s*\n?", "", current_chunk.strip()
            )
            is_empty = not bool(chunk_without_date.strip())
            if is_empty:
                continue

            document = gen_document_from_chunk(
                current_chunk=current_chunk,
                metadata=doc.metadata,
                written_date=written_date,
            )
            split_docs.append(document)

    return split_docs


# まず日付パターンで分割
date_split_docs = split_by_date_pattern(docs)
print(f"日付パターンで分割: {len(date_split_docs)}個のドキュメント")

for date_split_doc in date_split_docs:
    print("--------------------------------")
    print(f"date_split_doc: {date_split_doc}")
    print("--------------------------------")

# その後、RecursiveCharacterTextSplitterで細かく分割
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # 適切なサイズに調整
    chunk_overlap=200,  # オーバーラップを設定
    add_start_index=True,
    separators=["\n\n", "\n", "。", " ", ""],  # 日本語に適した区切り文字
)
all_splits = text_splitter.split_documents(date_split_docs)

# print(f"{len(all_splits)}のサブドキュメントに分割されました。")

# for i, all_split in enumerate(all_splits):
#     print(f"{i}番目のall_split: {all_split.page_content}")

# document_ids = vector_store.add_documents(documents=all_splits)
# print(f"ドキュメントが追加されました: {document_ids}")
