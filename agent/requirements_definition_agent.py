import operator
from typing import Annotated, Sequence, TypedDict
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from langgraph.graph import START, Pregel,StateGraph
from langgraph.constants import Send
from qdrant_client.models import ScoredPoint

from agent.prompts import ReqDefAgentPrompts

# settings.py
class Settings(BaseSettings):
  openai_api_key: str
  openai_model: str
  openai_model: str

# models.py
class SearchOutput(BaseModel):
  file_name: str = Field(description="The file name")  
  content: str = Field(description="The content of the file")

  @classmethod
  def from_hit(cls, hit: dict) -> "SearchOutput":
    return cls(
      file_name=hit["_source"]["file_name"], content=hit["_source"]["content"]
    )
  
  @classmethod
  def from_point(cls, point: ScoredPoint) -> "SearchOutput":
    if point.payload is None:
      raise ValueError("Payloadがありません")
    return cls(
      file_name=point.payload["file_name"], content=point.payload["content"]
    )

class ToolResult(BaseModel):
  tool_name: str = Field(..., description="ツールの名前")
  args: str = Field(..., description="ツールの引数")
  results: list[SearchOutput] = Field(..., description="ツールの結果")

class ReflectionResult(BaseModel):
  advice: str = Field(
    ...,
    description="評価がNGの場合は、別のツールを試す、別の文言でツールを試すなど、なぜNGなのかとどうしたら改善できるかを考えアドバイスを作成してください。\
アドバイスの内容は過去のアドバイスと計画内容の他のサブタスクと重複しないようにしてください。\
アドバイスの内容をもとにツール選択・実行からやり直します。"
  )
  is_completed: bool = Field(
    ...,
    description="ツールの実行結果と回答から、サブタスクに対して正しく回答できているかの評価結果",
  )

class Subtask(BaseModel):
  task_name: str = Field(..., description="サブタスクの名前")
  tool_results: list[list[ToolResult]] = Field(..., description="サブタスクの結果")
  reflection_results: list[ReflectionResult] = Field(..., description="サブタスクの評価結果")
  is_completed: bool = Field(..., description="サブタスクが完了しているかどうか")
  subtask_answer: str = Field(..., description="サブタスクの回答")
  challenge_count: int = Field(..., description="サブタスクの挑戦回数")



class AgentState(TypedDict):
  question: str
  plan: list[str]
  settings: Settings
  current_step: int
  subtask_results: Annotated[Sequence[Subtask], operator.add]
  last_answer: str

# # RequirementsDefinitionAgent
class ReqDefAgent:
  def __init__(
    self,
    settings: Settings,
    tools: list = [],
    prompts: ReqDefAgentPrompts = ReqDefAgentPrompts()
  ) -> None:
    self.settings = settings

  # Pregel: 大規模グラフ処理のための計算モデル
  def create_graph(self) -> Pregel:
    workflow = StateGraph(AgentState)

    workflow.add_node("create_plan", self.create_plan)
    workflow.add_node("execute_subtasks", self.execute_subtasks)
    workflow.add_node("create_answer", self.create_answer)

    workflow.add_edge(START, "create_plan")
    workflow.add_conditional_edges("create_plan", self._should_continue_exec_subtasks)
    workflow.add_edge("execute_subtasks", "create_answer")
    workflow.set_finish_point("create_answer")

    app = workflow.compile()
    return app

  def create_plan(self, state: AgentState) -> dict:
    pass

  def execute_subtasks(self, state: AgentState) -> dict:
    pass

  def crate_answer(self, state: AgentState) -> dict:
    pass

  def _should_continue_exec_subtasks(self, state: AgentState) -> list:
    return [
      Send(
        "execute_subtasks",
        {
          "question": state["question"],
          "plan": state["plan"],
          "current_step": idx
        }
      )
      for idx, _ in enumerate(state["plan"])
    ]