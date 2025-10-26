from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage, HumanMessage
import json, os
from langgraph.graph import StateGraph, END
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator

load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# モデルのセットアップ
tools = [TavilySearch(max_results=1)]

# ツール辞書を作成
tools_dict = {tool.name: tool for tool in tools}

# トークンをストリーミングする
model = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY, streaming=True, model="gpt-4o-mini")
model = model.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def should_continue(state: AgentState) -> str:
    messages = state['messages']
    last_message = messages[-1]
    # tool_callsがある場合は続行
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "continue"
    else:
        return "end"

def call_model(state: AgentState) -> AgentState:
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

def call_tool(state: AgentState) -> AgentState:
    messages = state['messages']
    last_message = messages[-1]
    
    # tool_callsから情報を取得
    tool_calls = last_message.tool_calls
    
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call['name']
        tool_input = tool_call['args']
        
        # ツール辞書から該当ツールを取得して実行
        if tool_name in tools_dict:
            tool = tools_dict[tool_name]
            response = tool.invoke(tool_input)
        else:
            response = f"ツール '{tool_name}' が見つかりません"
        
        # 応答を使って ToolMessageを作成
        tool_message = ToolMessage(
            content=str(response),
            name=tool_name,
            tool_call_id=tool_call['id']
        )
        results.append(tool_message)
    
    return {"messages": results}

workflow = StateGraph(AgentState)

# 循環する2つのノードを定義
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

# エントリーポイントとして`agent`を定義
workflow.set_entry_point("agent")

# 条件付きエッジを追加
workflow.add_conditional_edges(
    # 開始ノードを定義
    "agent",
    # 次に呼び出されるノードを決定する関数を渡す
    should_continue,
    # 最後に、マッピングを渡します。
    # キーは文字列で、値は他のノードです。
    # END はグラフが終了することを示す特別なノードです。
    # `should_continue` を呼び出し、その出力がこのマッピングのキーに一致するものに基づいて、
    # 次に呼び出されるノードが決定されます。
    {
        # `continue`の場合、`action`ノードを呼び出し
        "continue": "action",
        "end": END,
    }
)

# `action` から `agent` への通常のエッジを追加します。
# これは `action` が呼び出された後、次に `agent` ノードが呼ばれることを意味します。
workflow.add_edge('action', 'agent')

app = workflow.compile()

def main():
    inputs = {"messages": [HumanMessage(content="新宿の今日の天気は？")]}
    print(app.invoke(inputs))
