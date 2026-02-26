# graph.py
from typing import TypedDict, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

# Import from our local modules
from schema import IntentSkeleton
from prompts import get_intent_extraction_prompt
from llm import get_llm  
class IntentState(TypedDict):
    query: str
    skeleton: Optional[IntentSkeleton]

def extract_intent_node(state: IntentState):
    query = state["query"]

    # Now, if you change llm.py, the graph automatically updates.
    llm = get_llm(temperature=0)
    
    # Bind the schema
    structured_llm = llm.with_structured_output(IntentSkeleton)

    # Invoke
    response = structured_llm.invoke([
        SystemMessage(content=get_intent_extraction_prompt()),
        HumanMessage(content=query)
    ])

    return {"skeleton": response}

def build_graph():
    builder = StateGraph(IntentState)
    builder.add_node("extract_intent", extract_intent_node)
    builder.add_edge(START, "extract_intent")
    builder.add_edge("extract_intent", END)
    return builder.compile()