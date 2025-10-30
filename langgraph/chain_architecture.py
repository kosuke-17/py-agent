from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from langgraph import graph
from langgraph.graph.state import START, END, StateGraph
from langgraph.graph.message import add_messages

# SQLクエリを生成するためのモデル
model_low_temp = ChatOpenAI(temperature=0.1)
# 自然言語の出力を生成するためのモデル
model_high_temp = ChatOpenAI(temperature=0.7)

class State(StateGraph):
  messages: Annotated[list, add_messages]
  # 入力
  user_query: str
  # 出力
  sql_query: str
  sql_explain:str

class Input(TypedDict):
  user_query: str

class Output(TypedDict):
  sql_query: str
  sql_explain:str

generate_prompt = SystemMessage(
  """あなたはユーザーの質問に基づいてSQLクエリを生成する有能なデータアナリストです"""
)

def generate_sql(state: State) -> State:
  user_message = HumanMessage(state["user_query"])
  messages = [generate_prompt, *state["messages"], user_message]
  res = model_low_temp.invoke(messages)
  return {
    "sql_query": res.content,
    # 会話履歴を更新する
    "messages": [user_message, res],
  }

explain_prompt = HumanMessage(
  """あなたはユーザーにSQLクエリを説明する有能なデータアナリストです。"""
)

def explain_sql(state: State) -> State:
  messages = [
    explain_prompt,
    # ユーザークエリと前段で生成したSQLクエリを含む
    *state["message"],
  ]
  res = model_high_temp.invoke(messages)
  return {
    "sql_explanation": res.content,
    # 会話履歴を更新する
    "messages": res
  }

builder = StateGraph(State, input=Input, output=Output)
builder.add_node("generate_sql", generate_sql)
builder.add_node("explain_sql", explain_sql)
builder.add_edge(START, "generate_sql")
builder.add_edge("generate_sql", "explain_sql")
builder.add_edge("explain_sql", END)

graph = builder.compile()

# SQLを生成し、そのSQLを解説する
def main():
  graph.invoke({
    "user_query": "各製品の売り上げをいくらですか？"
  })