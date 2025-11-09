import operator
from typing import Annotated, Sequence, TypedDict
from langgraph.graph import START, Pregel,StateGraph
from langgraph.constants import Send

from agent.models import Subtask
from agent.prompts import ReqDefAgentPrompts
from agent.settings import Settings

class AgentState(TypedDict):
  question: str
  plan: list[str]
  settings: Settings
  current_step: int
  subtask_results: Annotated[Sequence[Subtask], operator.add]
  last_answer: str

# RequirementsDefinitionAgent
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