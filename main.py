# from check_typos import check_typos
# from tavily_search.main import main as tavily_search_main
from agent.requirements_definition_agent import ReqDefAgent
from agent.settings import Settings
# from vector_paython.main import main as vector_paython_main
# from langgragh_practice.main import main as langgragh_practice_main  


def main():
    settings = Settings()
    agent = ReqDefAgent(
      settings=settings,
      tools=[]
    )
    graph = agent.create_graph()
    initial_state = {
        "question": "TODOアプリを作成したいです。",
        "plan": [],
        "settings": settings,
        "current_step": 0,
        "subtask_results": [],
        "last_answer": ""
    }
    result = graph.invoke(initial_state)
    print("結果:", result)
    # vector_paython_main()
    # langgragh_practice_main()

if __name__ == "__main__":
    main()
