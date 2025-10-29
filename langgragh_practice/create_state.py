from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
import os

class State(TypedDict):
  # 型ヒント、型定義をするためのも
  # messagesの型はlist
  # アノテーションに指定した`add_messages`はこのステートの更新方法を定義
  # この例では、既存メッセージに置き換えるのではなく、listに追記する
  messages: Annotated[list, add_messages]

builder = StateGraph(State)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def chatbot(state: State):
  answer = model.invoke(state["messages"])
  return {"messages": [answer]}

# 第一引数はノードの一意の名前、第二引数は実行する関数または実行可能オブジェクト(Runnable Object)
builder.add_node("chatbot", chatbot)

builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)

graph = builder.compile()

def main():
  image_data = graph.get_graph().draw_mermaid_png()
  script_dir = os.path.dirname(os.path.abspath(__file__))
  file_path = os.path.join(script_dir, "graph_diagram.png")
  with open(file_path, "wb") as f:
    f.write(image_data)
  print(f"PNG ファイルを保存しました: {file_path}")

if __name__ == "__main__":
  main()