import json
import os
from typing import Literal, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore
from tavily import TavilyClient  # type: ignore[import-untyped]

load_dotenv()

# Tavily クライアント初期化
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))
store = InMemoryStore()


# ツール定義
@tool
def search_apartments(
    location: str,
    bedrooms: Optional[int] = None,
    price_range: Optional[str] = None,
    pet_friendly: Optional[bool] = None,
    topic: Literal["general", "news"] = "general",
) -> str:
    """
    Tavily を使用して賃貸物件を検索します。

    Args:
        location: 検索エリア（例: 渋谷、新宿、東京都）
        bedrooms: 寝室数（1、2、3 など、オプション）
        price_range: 家賃の範囲（例: "10万-15万円"、オプション）
        pet_friendly: ペット可かどうか（True の場合、ペット可物件を検索）
        topic: 検索トピック（general または news）
    """
    print("search_apartmentsが呼ばれました")
    print(f"location: {location}")
    print(f"bedrooms: {bedrooms}")
    print(f"price_range: {price_range}")
    print(f"pet_friendly: {pet_friendly}")
    print(f"topic: {topic}")
    # 検索クエリを構築
    query_parts = [f"{location}の賃貸物件"]

    if bedrooms:
        query_parts.append(f"{bedrooms}寝室")
    if price_range:
        query_parts.append(price_range)
    if pet_friendly:
        query_parts.append("ペット可")

    query = " ".join(query_parts)

    try:
        # Tavily で検索
        results = tavily_client.search(
            query, max_results=5, topic=topic, include_raw_content=True
        )

        # 結果をフォーマット
        formatted_results = []
        for result in results.get("results", []):
            formatted_results.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "source": result.get("source", ""),
                }
            )

        return json.dumps(formatted_results, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"検索エラー: {str(e)}"}, ensure_ascii=False)


# エージェント作成
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent: Runnable = create_agent(
    model=model,
    tools=[search_apartments],
    store=store,
    system_prompt="""
    あなたは賃貸物件検索の専門家です。ユーザーの要望に最適な物件を見つけるのを手伝います。
    
    ガイドライン：
    - ユーザーの要望を整理してから検索してください（地域、予算、間取り、ペット可など）
    - ペット可の物件を探す場合は、pet_friendly パラメータを True に設定してください
    - 検索結果から有用な情報を抽出し、ユーザーフレンドリーに説明してください
    """,
)


# 使用例
if __name__ == "__main__":
    print("=== 例 1: 京王線で13万以上で18万以下のペット可物件を検索 ===")
    result1 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "京王線で13万以上で18万以下のペット可な2LDK以上の物件を探してください",
                }
            ]
        }
    )
    print(result1["messages"][-1].content)
    print("\n" + "=" * 50 + "\n")
