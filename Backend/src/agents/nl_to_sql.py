import logging

from src.utils.llm_router import llm_router
from src.utils.config_loader import load_yaml
from src.agents.memory_manager import get_memory_context
import yaml
from string import Template
from typing import List

import re
from sqlglot import parse_one, exp
from src.db.client import SupabaseDB

async def generate_sql(user_message: str, electricity_id: str, memory_context: dict) -> str:
    """ Generate SQL query from natural language using LLM """

    # Load prompt template

    with open("src/prompts/sql_generator.yaml", "r") as f:
        prompt_template = yaml.safe_load(f)["instruction"]

    # Inject electricity_id into the prompt
    prompt = Template(prompt_template).substitute(electricity_id=electricity_id)
    
    # Add memory contexts if available
    if memory_context.get("recent_conversation"):
        context_str = "\nRecent Conversation:\n" + "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in memory_context["recent_conversation"]]
            )
        prompt += context_str

    # Call LLM
    full_prompt = f"{prompt}\n\nUser question: {user_message}"
    sql = await llm_router.chat_completion(prompt=full_prompt, system_prompt="You are a SQL generator. Output ONLY valid PostgreSQL SELECT statements.")

    # Remove markdown code block formatting
    sql = sql.strip().strip("```sql").strip("```").strip()
    return sql


def execute_sql_query(sql: str, electricity_id: str) -> list[dict]:
    """
    Execute validated SQL via secure RPC.
    Uses sqlglot to safely extract columns & WHERE conditions.
    
    Args:
        sql: Validated SELECT query string
        electricity_id: User's ID for filtering (passed to RPC)
    """
    try:

        logging.info(f"🔍 Executing SQL for {electricity_id}: {sql[:100]}...")

        # 1. Extract columns from SELECT clause
        select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.I | re.DOTALL)
        if not select_match:
            logging.warning("⚠️ Could not parse SELECT columns, using defaults")
            columns = ["month", "balance", "paid_amount"]
        else:
            col_str = select_match.group(1).strip()
            # Handle "SELECT *" or "SELECT balance, month"
            if col_str == "*":
                columns = ["units", "month", "price", "paid_amount", "balance"]
            else:
                # Split by comma, clean up column names
                columns = [c.strip().lower() for c in col_str.split(',')]
                # Filter to only allowed columns
                allowed = {"units", "month", "price", "paid_amount", "balance"}
                columns = [c for c in columns if c in allowed]
                if not columns:
                    columns = ["month", "balance", "paid_amount"]
        
        # 2. Extract simple WHERE conditions (exclude electricity_id)
        # Look for month = 'YYYY-MM' pattern ex - 2024-05
        month_match = re.search(r"month\s*=\s*['\"]?(\d{4}-\d{2})", sql, re.I)
        where_clause = f"month = '{month_match.group(1)}'" if month_match else None
        
        # 3. Call secure RPC
        logging.info(f" RPC params: electricity_id={electricity_id}, columns={columns}, where={where_clause}")
        
        client = SupabaseDB.init()
        result = client.rpc("exec_secure_select", {
            "p_electricity_id": electricity_id,
            "p_columns": columns, 
            "p_where_clause": where_clause
        }).execute()
        
        # 4. Handle response
        if hasattr(result, 'error') and result.error:
            logging.error(f" RPC error: {result.error}")
            return [{"error": f"Database error: {result.error.get('message', 'Unknown')}"}]
        
        data = result.data if hasattr(result, 'data') else None
        logging.info(f" RPC returned {len(data) if data else 0} rows")
        return data or []
        
    except Exception as e:
        import traceback
        logging.error(f" execute_sql_query exception: {type(e).__name__}: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return [{"error": f"Query failed: {str(e)[:100]}"}]