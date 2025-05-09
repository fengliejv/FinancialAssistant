
import json
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

from config.config import Config

MEMORY_KEY = "chat_history"


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

# 

def generate_sys_prompt(reports):
    """
    Generates a system prompt with the given reports parameter.

    Args:
        reports (str): The reports parameter to be included in the system prompt.

    Returns:
        str: The formatted system prompt.
    """
    return f'''
You are a professional secretary, mainly engaged in the management work related to weekly reports. 

## knowledge
Here are the reports you hava:
{reports}

##Rules
1. If users ask a question unrelated to reports, you should politely refuse to answer. 
2. Respond in the same language as the user's input.
    '''

def load_reports(directory):
    reports = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                file_content = json.load(file)
                reports[filename[:-5]] = file_content  # Store each file's content in a dictionary with the filename as the key
    return reports

reports_directory = 'production/reports'


def get_agent_executor(session_id):
    reports = load_reports(reports_directory)
    # sys_prompt = generate_sys_prompt(reports)
    sys_prompt = generate_sys_prompt(reports).replace('"', "'").replace("{","{{").replace("}","}}")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                sys_prompt,
            ),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    # llm = ChatOpenAI(model=Config.MODEL, temperature=0, base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',api_key='sk-1c8a6497272b42ba9fbb232ed8a82c34',stream=True,stream_options={"include_usage": True})
    llm = ChatOpenAI(model=Config.MODEL, temperature=0, base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',api_key='sk-1c8a6497272b42ba9fbb232ed8a82c34')
    search = TavilySearchResults()
    tools = [search]
    # tools = []
    llm_with_tools = llm.bind_tools(tools)

    agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x[MEMORY_KEY],
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    message_history = RedisChatMessageHistory(
        url=Config.REDIS_URL, ttl=600, session_id= session_id
    )
    # message_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        lambda session: message_history,
        input_messages_key="input",
        history_messages_key=MEMORY_KEY,
    )

    return agent_with_chat_history



