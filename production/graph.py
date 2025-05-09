from langchain_community.tools.tavily_search import TavilySearchResults

tools = [TavilySearchResults(max_results=3)]

# from langchain import hub
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langgraph.prebuilt import create_react_agent

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="Pro/deepseek-ai/DeepSeek-V3", base_url='https://api.siliconflow.cn/v1',api_key='sk-jhxqzgvbrlhovsxxukzcywmwiyicfrhsgnqhiealutvcdfxm'
                    )

prompt = "You are a helpful assistant."
agent_executor = create_react_agent(llm, tools, prompt=prompt)

import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str

from pydantic import BaseModel, Field


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


from langchain_core.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
""",
        ),
        ("placeholder", "{messages}"),
    ]
)
llm = ChatOpenAI(model="Pro/deepseek-ai/DeepSeek-V3", base_url='https://api.siliconflow.cn/v1',api_key='sk-jhxqzgvbrlhovsxxukzcywmwiyicfrhsgnqhiealutvcdfxm'
                    )
# jsonllm = llm.bind(response_format={"type": "json_object"})
planner = planner_prompt | llm.with_structured_output(Plan)
# planner = planner_prompt | ChatOpenAI(model="gpt-4o",api_key='sk-proj-wTjZW0M0Ip6rkVegiLx8T3B').with_structured_output(Plan)

from typing import Union


class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


replanner_prompt = ChatPromptTemplate.from_template(
    """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{input}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
)


replanner = replanner_prompt | ChatOpenAI(model="Pro/deepseek-ai/DeepSeek-V3", base_url='https://api.siliconflow.cn/v1',api_key='sk-jhxqzgvbrlhovsxxukzcywmwiyicfrhsgnqhiealutvcdfxm'
                    ).with_structured_output(Act)


from langgraph.graph import END


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""For the following plan:
{plan_str}\n\nYou are tasked with executing step {1}, {task}."""
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        return {"plan": output.action.steps}


def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "agent"

from langgraph.graph import StateGraph, START

workflow = StateGraph(PlanExecute)

# Add the plan node
workflow.add_node("planner", plan_step)

# Add the execution step
workflow.add_node("agent", execute_step)

# Add a replan node
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")

# From plan we go to agent
workflow.add_edge("planner", "agent")

# From agent, we replan
workflow.add_edge("agent", "replan")

workflow.add_conditional_edges(
    "replan",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
    ["agent", END],
)

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile()



# from IPython.display import Image, display

# display(Image(app.get_graph(xray=True).draw_mermaid_png()))


import asyncio

async def process_events():
    config = {"recursion_limit": 50}
    inputs = {"input": "总结4月的第三周的 部门关键事项"}
    # inputs = {"input": "Hello"}
    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

# To run the async function
if __name__ == "__main__":
#     client = OpenAI(
#     api_key='sk-1c8a6497272b42ba9fbb232ed8a82c34',
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# )

#     completion = client.chat.completions.create(
#     model="qwen-max",
#     messages=[
#             {
#                 "role": "system",
#                 "content": f"""Extract name, age, email, and hobby (array type), and output JSON containing the info layer and hobby array."""
#             },
#             {
#                 "role": "user",
#                 "content": "Hello everyone, my name is Dave, I am 34 years old, my email is dave@example.com, and I like playing basketball and traveling", 
#             },
#         ],
#         response_format={"type": "json_object"},
#     )

#     json_string = completion.choices[0].message.content
#     print(json_string)

#     planner.invoke(
#     {
#         "messages": [
#             ("user", "what is the hometown of the current Australia open winner?")
#         ]
#     },
# )
    asyncio.run(process_events())