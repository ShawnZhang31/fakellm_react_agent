"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from datetime import UTC, datetime
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt
import uuid


from react_agent.configuration import Configuration
from react_agent.state import InputState, State
from react_agent.tools import TOOLS, search
from react_agent.utils import load_chat_model
from react_agent.chatmodel import FakeModel


# Define the function that calls the model


def call_model(state: State) -> Command[Literal["human_review", "subgraph"]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = Configuration.from_context()

    # Initialize the model with tool binding. Change the model or add more tools here.
    # model = load_chat_model(configuration.model).bind_tools(TOOLS)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt.format(
        system_time=datetime.now(tz=UTC).isoformat()
    )

    # Get the model's response
    response = cast(
        AIMessage,
        FakeModel.invoke(
            [{"role": "system", "content": system_message}, *state.messages]
        ),
    )
    # 为了确保graph多次执行的时候，不会因为消息的id相同，使得state update的时候更新的id不对，这里使用动态message id
    response.id = str(uuid.uuid4())

    if response.tool_calls:
        # If the model wants to use a tool, we need to handle it
        return Command(
            goto ="human_review",
            update={"messages": [response]})
    else:
        return Command(
            goto ="subgraph",
            update={"messages": [response]})



def tool_action(state: State) -> Command[Literal["call_model"]]:
    """Perform a tool action.
    """
    last_message = state.messages[-1]
    tool_call_data = last_message.tool_calls[0]
    tool_result = search(tool_call_data["args"]["query"])

    tool_message = ToolMessage(
        id=str(uuid.uuid4()),
        content=tool_result,
        tool_call_id=tool_call_data["id"],
        tool_name=tool_call_data["name"],
    )

    return Command(
        goto="call_model",
        update={"messages": [tool_message]},
    )

def human_review_node(state: State) -> Command[Literal["call_model", "tools"]]:
    """Handle human review of the model's output.

    This function is a placeholder for human review logic. It currently returns the
    model's output without any modifications.

    Args:
        state (State): The current state of the conversation.

    Returns:
        Command: A command to continue the conversation with the model's output.
    """
    # In a real implementation, this would involve human review logic
    # print(state.messages)
    last_message = state.messages[-1]
    tool_call = last_message.tool_calls[0]

    # 这是用于提供给用户确信的信息，通过Command来实现(resume=<human_review>)
    human_review = interrupt(
        {
            "question": "工具调用正确吗？",
            "tool_call": tool_call
        }
    )

    review_action = human_review["action"]
    review_data = human_review.get("data")

    # 如果用户同意执行
    if review_action == "continue":
        # 这里可以添加更多的逻辑来处理用户的反馈
        return Command(goto="tools")
    elif review_action == "update":
        updated_message = AIMessage(
            id=last_message.id,
            content=last_message.content,
            tool_calls=[{
                "id": tool_call["id"],
                "name": tool_call["name"],
                # 这里使用人工更新的参数执行
                "args": review_data,
            }],
        )
        return Command(
            goto="tools",
            update={"messages": [updated_message]})
    elif review_action == "feedback":
        tool_message = ToolMessage(id=str(uuid.uuid4()),
                                   content = review_data,
                                   tool_call_id = tool_call["id"],
                                   name = tool_call["name"])
        return Command(goto="call_model",
                       update={"messages": [tool_message]})
    else:
        updated_message = HumanMessage(content=f"拒绝调用工具{tool_call['name']}")
        return Command(goto="call_model",
                       update={"messages": [updated_message]}) 


def subgraph_node(state:State):
    return Command(
        goto="__end__",
        update={
            "messages": [
                AIMessage(
                    id=str(uuid.uuid4()),
                    content="子图执行完毕，返回主图继续执行"
                )
            ]
        }
    )

subgraph_builder = StateGraph(State)
subgraph_builder.add_node("subgraph_node", subgraph_node)
subgraph_builder.add_edge("__start__", "subgraph_node")
subgraph = subgraph_builder.compile(name="subgraph")

# Define a new graph

builder = StateGraph(State, input=InputState, config_schema=Configuration)

# Define the two nodes we will cycle between
builder.add_node(call_model)
builder.add_node("tools", tool_action)
builder.add_node("human_review", human_review_node)
builder.add_edge("__start__", "call_model")
builder.add_node("subgraph", subgraph)
builder.add_edge("subgraph", "__end__")

# Compile the builder into an executable graph
graph = builder.compile(name="ReAct Agent")
