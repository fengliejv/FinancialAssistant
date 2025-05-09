from langchain_openai import ChatOpenAI

import json
import os


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
1. If users asks a question unrelated to reports, you should politely refuse to answer. 
2. Respond in the same language as the user's input.
3. 
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
reports = load_reports(reports_directory)

sys_prompt = generate_sys_prompt(reports).replace('"', "'").replace("{","{{").replace("}","}}")
# llm = ChatOpenAI(model="gpt-4o")
# response = llm.invoke([
#     {"role": "system", "content": sys_prompt},
#     {"role": "user", "content": "hello"}
# ])
# print(response)


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", sys_prompt),
    ("user", "追踪c4Agent的工作情况")
])
model = ChatOpenAI(model="gpt-4o")
output_parser = StrOutputParser()

chain = prompt | model | output_parser

question = "追踪c4Agent的工作情况"
# chain.invoke({"question": question})
output = chain.invoke({})
print(output)



# nlp 2 sql tool
# engine = create_engine('mysql+pymysql://username:password@host:port/database')
# db = SQLDatabase(engine)
# sql_tool = QuerySQLDataBaseTool(db=db)

# 3. NLP to RAG Tool
# 假设你已经有一个向量库 vectorstore
# retriever = vectorstore.as_retriever()
# rag_tool = create_retriever_tool(
#     retriever,
#     name="dify_rag",
#     description="RAG 检索 dify 平台知识"
# )

# 4. 注册工具
# tools = [sql_tool, rag_tool]

# 5. 创建 Agent
# graph = create_react_agent(llm, tools)
# graph = create_react_agent(llm)
