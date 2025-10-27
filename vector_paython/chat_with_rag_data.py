from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from langchain_postgres import PGEngine, PGVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

connection_string = 'postgresql+psycopg://langchain:langchain@localhost:6024/langchain'

engine = PGEngine.from_connection_string(connection_string)
vectorstore = PGVectorStore.create_sync(engine=engine, table_name="docs", embedding_service=OpenAIEmbeddings())
vectorstore_summaries = PGVectorStore.create_sync(engine=engine, table_name="summaries_documents", embedding_service=OpenAIEmbeddings())

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
  """
  EC2 (Amazon Linux 2023) から CloudWatch にアクセスログを送信する手順を以下に示します。
  {context}

  ユーザーの質問に対して、上記のドキュメントを参考に回答してください。
  もし、EC2以外の質問に対しては、「EC2以外の質問には対応していません。」と回答してください。
  {question}
  """
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@chain
def qa(input):
  # 関連ドキュメントを取得
  docs = retriever.invoke(input)
  # プロンプトを整形
  formatted_prompt = prompt.invoke({"context": docs, "question": input})
  # 回答を生成
  answer =llm.invoke(formatted_prompt)
  return answer

def main():
  result = qa.invoke("EC2 へのアクセスログを CloudWatch に送信する手順を教えてください。関西弁で回答してください。")
  print(result)

if __name__ == "__main__":
  main()