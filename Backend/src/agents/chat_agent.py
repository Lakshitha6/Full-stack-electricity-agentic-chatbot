from typing import TypedDict, Annotated, List, Optional
from src.agents.nl_to_sql import generate_sql, execute_sql_query
from src.agents.memory_manager import get_memory_context
from src.utils.llm_router import llm_router
from src.utils.config_loader import load_yaml
from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

import yaml

class AgentState(TypedDict):

    electricity_id: str
    user_message: str
    session_id: Optional[str]
    memory_context: dict
    generated_sql: Optional[str]
    sql_result: Optional[List[dict]]
    final_response: str
    error: Optional[str]
    


def load_memory(state: AgentState) -> AgentState:
    """ Retrieve medium + long-term memory """

    context = get_memory_context(state["electricity_id"], state.get("session_id"))
    state["memory_context"] = context
    return state


async def generate_sql_node(state: AgentState) -> AgentState:

    """Generate SQL from natural language"""

    try:
        sql = await generate_sql(
            user_message=state["user_message"],
            electricity_id=state["electricity_id"],
            memory_context=state["memory_context"]
        )
        state["generated_sql"] = sql
        return state
    except Exception as e:
        state["error"] = f"SQL generation failed: {str(e)}"
        return state


def validate_and_execute_sql(state: AgentState) -> AgentState:
    """ Validate and execute SQL query via secure RPC"""

    if state.get("error"):
        return state

    from src.utils.sql_validator import sql_validator

    is_valid, validated_sql = sql_validator.validate(state["generated_sql"],state["electricity_id"])

    if not is_valid:
        state["error"] = f"SQL validation failed: {validated_sql}"
        return state

    try:

        from src.agents.nl_to_sql import execute_sql_query
        
        data = execute_sql_query(validated_sql, state["electricity_id"])
        state["sql_result"] = data
        return state
    except Exception as e:
        state["error"] = f"SQL execution failed: {str(e)}"
        return state


async def generate_response(state: AgentState) -> AgentState:
    """ Generate final human-readable response """
    
    if state.get("error"):
        state["final_response"] = f"Error: {state['error']}. Please rephrase or check your profile."
        return state

    # Load personalization prompt
    with open("src/prompts/personalization.yaml", "r") as f:
        prompts = yaml.safe_load(f)

    system_prompt = prompts["instruction"] + "\n\n" + prompts["preference_injection"].format(
        preferred_language=state["memory_context"].get("preferred_language", "en"),
        response_detail_level=state["memory_context"].get("response_detail_level", "concise"),
        common_queries=", ".join(state["memory_context"].get("common_queries", [])[:3])
    )

    user_prompt = f"""
                        User asked: "{state['user_message']}"
                        Query result: {state['sql_result']}
                        
                        Provide a helpful, personalized response.
                    """

    try:
        response = await llm_router.chat_completion(prompt=user_prompt, system_prompt=system_prompt)
        state["final_response"] = response

    except Exception as e:
        state["final_response"] = "I'm having trouble generating a response. Please try again."
    
    return state


def route_logic(state: AgentState) -> str:
    """ Decide next node based on state """

    if state.get("error"):
        return "generate_response"
        
    if not state.get("generated_sql"):
        return "generate_sql_node"
        
    if not state.get("sql_result"):
        return "validate_and_execute_sql"
        
    return "generate_response"


# build workflow
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("load_memory", load_memory)
workflow.add_node("generate_sql_node", generate_sql_node)
workflow.add_node("validate_and_execute_sql", validate_and_execute_sql)
workflow.add_node("generate_response", generate_response)

# Edges
workflow.add_edge(START, "load_memory")

workflow.add_conditional_edges(
    "load_memory",
    route_logic,
    {
        "generate_sql_node": "generate_sql_node",
        "generate_response": "generate_response"
    }
)

workflow.add_edge("generate_sql_node", "validate_and_execute_sql")
workflow.add_edge("validate_and_execute_sql", "generate_response")
workflow.add_edge("generate_response", END)

# Compile with memory
agent = workflow.compile(checkpointer=MemorySaver())