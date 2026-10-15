
from langgraph.prebuilt import create_react_agent



from llm.gemini import llm
from security import pending_actions
from tools.terminal import run_command
from tools.filesystem import (
    delete_file,
    list_directory,
    read_file,
    search_files,
    create_file
)
from tools.git_tools import (
    git_status,
    git_diff,
    git_log,
)
from agent.prompts import SYSTEM_PROMPT

import security.pending_actions as pending_actions



tools = [
    run_command,
    list_directory,
    read_file,
    search_files,
    git_status,
    git_diff,
    git_log,
    delete_file,
    create_file
]

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT,
)
