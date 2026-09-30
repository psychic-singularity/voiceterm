from langgraph.prebuilt import create_react_agent

from llm.gemini import llm
from tools.terminal import run_command


tools = [run_command]

agent = create_react_agent(
    model=llm,
    tools=tools,
)
