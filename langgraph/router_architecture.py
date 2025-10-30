from typing import Annotated, Literal, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.vectorstores.in_memory import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


embeddings = OpenAIEmbeddings()

model_low_temp = ChatOpenAI(temperature=0.1)
model_high_temp = ChatOpenAI(temperature=0.7)

class State(TypedDict):
  messages: Annotated[list, add_messages]
  # 入力
  user_query: str
  # 出力
  domain: Literal["records", "insurance"]
  documents: list[Document]
  answer: str

class Input(TypedDict):
  user_query: str

class Output(TypedDict):
  documents: list[Document]
  answer: str

medical_records_store = InMemoryVectorStore.from_documents([], embeddings)
medical_records_retriever = medical_records_store.as_retriever()

insurance_faqs_store = InMemoryVectorStore.from_documents([], embeddings)
insurance_faqs_retriever = insurance_faqs_store.as_retriever()

router_prompt = SystemMessage(
  """
  ユーザーの問い合わせをどのドメインへルーティングするか決定してください。
  選択できるドメインは2つあります:
  - records: 患者の診断、治療、処方などの医療記録を含む。
  - insurance: 保険契約、請求、補償に関するFAQを含む。

  出力はドメイン名のみとしてください。
  """
)

def router_node(state: State) -> State:
  user_message = HumanMessage(state["user_query"])
  messages = [router_prompt, *state["messages"], user_message]
  res = model_low_temp.invoke(messages)
  return {
    "domain": res.content,
    # 会話履歴を更新
    "messages": [user_message, res]
  }

def pick_retriever(
  state: State
) -> Literal["retrieve_medical_records", "retrieve_insurance_faqs"]:
  if state["domain"] == "records":
    return "retrieve_medical_records"
  else:
    return  "retrieve_insurance_faqs"

def retrieve_medical_records(state: State) -> State:
  documents = medical_records_retriever.invoke(state["user_query"])
  return {
    "documents": documents
  }

def retrieve_insurance_faqs(state: State) -> State:
  documents = insurance_faqs_retriever.invoke(state["user_query"])
  return {
    "documents": documents
  }

medical_records_prompt = SystemMessage(
  """
  あなたは患者の診断、治療、処方などの医療記録に基づいて質問に答える有能な医療チャットbotです。
  """
)

insurance_faqs_prompt = SystemMessage(
  """
  あなたは保険契約、請求、補償に関するFAQに回答する有能な医療保険チャットbotです。
  """
)

def generate_answer(state: State) -> State:
  if state["domain"] == "records":
    prompt = medical_records_prompt
  else:
    prompt = insurance_faqs_prompt
  messages = [
    prompt,
    *state["messages"],
    HumanMessage(f"Documents: {state['documents']}")
  ]
  res = model_high_temp.invoke(messages)
  return {
    "answer": res.content,
    # 会話履歴を更新
    "messages": res,
  }

builder = StateGraph(State, input=Input, output=Output)
builder.add_node("router", router_node)
builder.add_node("retrieve_medical_records", retrieve_medical_records)
builder.add_node("retriece_infurance_faqs", retrieve_insurance_faqs)
builder.add_node("generate_answer", generate_answer)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", pick_retriever)
builder.add_edge("retrieve_medical_records", "generate_answer")
builder.add_edge("retriever_insurance_faqs", "generate_answer")
builder.add_edge("generate_answer", END)

graph = builder.compile()

def main():
  user_input = {
    "user_query": "新型コロナウイルスの治療は保証されていますか？"
  }
  # 出力ストリームには、グラフの実行時に動作した各ノードが返した値が含まれる
  for c in graph.stream(user_input):
    print(c)