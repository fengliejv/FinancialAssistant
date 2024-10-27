
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

from production.config.config import Config

MEMORY_KEY = "chat_history"


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

def get_agent_executor(session_id):
    sys_prompt ='''
    You are a professional financier with extensive financial expertise. 
    Your responsibility is to answer users' questions using your specialized financial knowledge.
    
    ##Rules
    1. If users asks a question unrelated to finance, you should politely refuse to answer. 
    2. Respond in the same language as the user's question.
    '''
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
    llm = ChatOpenAI(model=Config.MODEL, temperature=0)
    search = TavilySearchResults()
    tools = [search]
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