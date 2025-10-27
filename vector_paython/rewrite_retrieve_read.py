from langchain_core.runnables import chain
from langchain_postgres import PGEngine, PGVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
load_dotenv()

connection_string = 'postgresql+psycopg://langchain:langchain@localhost:6024/langchain'
engine = PGEngine.from_connection_string(connection_string)
vectorstore = PGVectorStore.create_sync(engine=engine, table_name="docs", embedding_service=OpenAIEmbeddings())
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
rewrite_prompt = ChatPromptTemplate.from_template(
  """
  Webの検索円時にでより良い回答を得るための検索クエリを生成し、クエリの末尾に'**'を付けてください。

  質問: {question} 回答:
  """
)

def parse_rewrite_output(message):
  return message.content.strip('"').split("**")[0]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

rewriter = rewrite_prompt | llm | parse_rewrite_output

@chain
def qa_rrr(input):
  # クエリを書き換える
  new_query = rewriter.invoke(input)
  # 関連ドキュメントを取得する
  docs = retriever.invoke(new_query)
  # プロンプトを整形
  formatted = prompt.invoke({ "context": docs, "question": input })
  # 回答を生成
  answer = llm.invoke(formatted)
  return answer

def main():
  result = qa_rrr.invoke("EC2 へのアクセスログを CloudWatch に送信する手順を教えてください。関西弁で回答してください。")
  print(result)

if __name__ == "__main__":
  main()