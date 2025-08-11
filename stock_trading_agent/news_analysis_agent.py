from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content and the tool_call_id
from langchain_core.messages import SystemMessage,HumanMessage # Message for providing instructions to the LLM
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from tools.pull_businesstoday import get_topic_news
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["LANGSMITH_PROJECT"]="NewsSummarizer"

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

tools = [get_topic_news]

model = ChatOpenAI(model = "gpt-4o").bind_tools(tools)

def stock_summarizer(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
        "You are a financial news summarizer working with web-scraped content from known news websites (e.g., Moneycontrol, Business Today)."
    )
    response = model.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # if model have done a tool call
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)
graph.add_node("our_agent", stock_summarizer)


tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

graph.add_edge("tools", "our_agent")

app = graph.compile()

prompts="""
Your task is to summarize the following news article(s) in a clear, concise, and fact-preserving way. Focus only on the essential information that would be relevant for financial markets, investors, or traders directly or indirectly .
DO:
- Extract and summarize actual financial and business news from each section
- Retain as much factual detail as possible: company names, numbers, dates, events, and announcements
- Write clearly and concisely but do **not omit important details** for the sake of brevity
- Include multiple companies, events, or sectors if mentioned
- Ignore only UI elements, ads, or obvious web clutter — everything else should be preserved
DO NOT:
- Perform sentiment analysis
- Classify or extract entities
- Infer or hallucinate missing details
"""

inputs = {"messages": [(f"user,{prompts}")]}


response=app.invoke(inputs)
for msg in response["messages"]:
    print(msg.pretty_print())

from langchain_core.prompts import ChatPromptTemplate

def create_supervisor_chain():
    """Creates the supervisor decision chain"""

    supervisor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a supervisor managing a team of agents:

1. Researcher - Gathers information and data
2. Analyst - Analyzes data and provides insights  
3. Writer - Creates reports and summaries

Based on the current state and conversation, decide which agent should work next.
If the task is complete, respond with 'DONE'.

Current state:
- Has research data: {has_research}
- Has analysis: {has_analysis}
- Has report: {has_report}

Respond with ONLY the agent name (researcher/analyst/writer) or 'DONE'.
"""),
        ("human", "{task}")
    ])
    return supervisor_prompt | model