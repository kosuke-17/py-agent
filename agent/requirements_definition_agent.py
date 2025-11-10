import operator
from typing import Annotated, Literal, Sequence, TypedDict
# from langchain_core.utils.function_calling import convert_to_openai_tool_calls
from langgraph.graph import START, END, StateGraph
# from langgraph.constants import Send
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from agent.models import Plan, ReflectionResult, SearchOutput, Subtask
from agent.prompts import ReqDefAgentPrompts
from agent.settings import Settings

class AgentState(TypedDict):
  question: str
  plan: list[str]
  settings: Settings
  current_step: int
  subtask_results: Annotated[Sequence[Subtask], operator.add]
  last_answer: str

class AgentSubGraphState(TypedDict):
  question: str
  plan: list[str]
  subtask: str
  is_completed: bool
  messages: list[ChatCompletionMessageParam]
  challenge_count: int
  # Sequenceは配列を意味するのでSearchOutputの2次元配列
  # 複数のノードからtool_resultsに値を追加する際に、operator.addにより既存の値に結合される
  tool_results: Annotated[Sequence[Sequence[SearchOutput]], operator.add]
  refrection_results: Annotated[Sequence[Sequence[ReflectionResult]], operator.add]
  subtask_answer: str

MAX_CHALLENGE_COUNT = 3

# RequirementsDefinitionAgent
class ReqDefAgent:
  def __init__(
    self,
    settings: Settings,
    tools: list = [],
    prompts: ReqDefAgentPrompts = ReqDefAgentPrompts()
  ) -> None:
    self.settings = settings
    self.tools = tools
    self.tool_map = {tool.name: tool for tool in tools}
    self.prompts = prompts
    self.client = OpenAI(api_key=self.settings.openai_api_key)

  # Pregel: 大規模グラフ処理のための計算モデル
  def create_graph(self):
    workflow = StateGraph(AgentState)

    workflow.add_node("create_plan", self.create_plan)
    # workflow.add_node("execute_subtasks", self.execute_subtasks)
    # workflow.add_node("create_answer", self.create_answer)

    workflow.add_edge(START, "create_plan")
    workflow.add_edge("create_plan", END)
    # workflow.add_conditional_edges("create_plan", self._should_continue_exec_subtasks)
    # workflow.add_edge("execute_subtasks", "create_answer")
    # workflow.set_finish_point("create_answer")

    app = workflow.compile()
    return app

  def create_plan(self, state: AgentState) -> dict:
    """計画を作成"""
    print("計画を生成する処理を開始🚀")

    print("OpenAIフォーマットにToolsを変換")
    # tools = [convert_to_openai_tool_calls(tool) for tool in self.tools]
    tools = []

    system_prompt = self.prompts.planner_system_prompt.format(
      tools=tools
    )
    user_prompt = self.prompts.planner_user_prompt.format(
      question=state["question"]
    )

    messages = [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ]
    print(f"メッセージプロンプト: {messages}")

    try:
      response = self.client.beta.chat.completions.parse(
        model=self.settings.openai_model,
        messages=messages,
        response_format=Plan,
        temperature=0,
        seed=0,
      )
    except Exception as e:
      print(f"エラー発生: {e}")
    
    plan = response.choices[0].message.parsed

    return {"plan": plan.steps}

  def execute_subtasks(self, state: AgentState) -> dict:
    pass

  def create_answer(self, state: AgentState) -> dict:
    pass

  # 生成された計画数分だけサブグラフを実行することが可能
  # def _should_continue_exec_subtasks(self, state: AgentState) -> list:
  #   return [
  #     Send(
  #       "execute_subtasks",
  #       {
  #         "question": state["question"],
  #         "plan": state["plan"],
  #         "current_step": idx
  #       }
  #     )
  #     for idx, _ in enumerate(state["plan"])
  #   ]

  # def _create_subgraph(self) -> Pregel:
  #   """
  #   サブグラフを作成

  #   Returns:
  #     Pregel: サブグラフ
  #   """
  #   workflow = StateGraph(AgentSubGraphState)

  #   workflow.add_node("select_tools", self.select_tools)
  #   workflow.add_node("execute_tools", self.execute_tools)
  #   workflow.add_node("create_subtask_andwer", self.create_subtask_answer)
  #   workflow.add_node("reflect_subtask", self.reflect_subtask)

  #   workflow.add_edge(START, "select_tools")
  #   workflow.add_edge("select_tools", "execute_tools")
  #   workflow.add_edge("execute_tools", "create_subtask_answer")
  #   workflow.add_edge("create_subtask_answer", "reflect_subtask")

  #   workflow.add_conditional_edges(
  #     "reflect_subtask",
  #     self._should_continue_exec_subtask_flow,
  #     {"continue": "select_tools", "end": END}
  #   )

  #   app = workflow.complie()
  #   return app

  # def _should_continue_exec_subtask_flow(
  #     self, state: AgentSubGraphState
  #   ) -> Literal["end", "continue"]:
  #   if state["is_completed"] or state["challenge_count"] >= MAX_CHALLENGE_COUNT:
  #     return "end"
  #   else:
  #     return "continue"