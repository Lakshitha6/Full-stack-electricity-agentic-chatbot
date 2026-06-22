import logging
import time
import json

from fastapi import Request, Response

from src.db.client import SupabaseDB
from src.utils.config_loader import load_yaml

logger = logging.getLogger(__name__)

async def audit_chat_request(request: Request, call_next):
    """
    Middleware: Log every chat API call for compliance & debugging.
    Logs: timestamp, electricity_id, endpoint, sql_used (if any), latency_ms, status

    """

    start_time = time.time()

    # Extract context from request
    electricity_id = request.query_params.get("electricity_id")

    if not electricity_id and request.method == "POST":
        try:
            body = await request.body()
            if body:
                data = json.loads(body)
                electricity_id = data.get("electricity_id")
        
        except (json.JSONDecodeError, UnicodeDecodeError, Exception) as e:
            logger.debug(f"Audit: Could not parse request body: {e}")
            electricity_id = None

    
    # Process request
    response: Response = await call_next(request)

    # Calculate latency
    latency_ms = round((time.time() - start_time) * 1000, 2)

    # Log to Supabase:
    try:
        config = load_yaml("db.yaml")["supabase"]

        # Extract SQL query from response if available
        sql_used = None

        if response.status_code == 200 and hasattr(response, "body"):
            try:
                import ast
                body_str = response.body.decode() if isinstance(response.body, bytes) else str(response.body)

                # Simple parse: look for "sql=" in metadata
                if '"sql"' in body_str or "'sql'" in body_str:
                    # Extract SQL substring
                    import re
                    sql_match = re.search(r"['\"]sql['\"]\s*:\s*['\"](.+?)['\"]", body_str)
                    if sql_match:
                        sql_used = sql_match.group(1)[:500]
            except:
                pass

        if electricity_id and electricity_id != "unknown" and electricity_id.startswith("ELEC-"):
            # Insert log into Supabase
            SupabaseDB.table("audit_logs").insert({
                "electricity_id": electricity_id,
                "endpoint": request.url.path,
                "method": request.method,
                "sql_used": sql_used,
                "latency_ms": latency_ms,
                "status_code": response.status_code,
                "user_agent": request.headers.get("user-agent", "")[:100],
                "ip_address": request.client.host if request.client else None
            }).execute()

        else:
            logger.info(f"Skipping audit log: invalid electricity_id='{electricity_id}'")
        
    except Exception as e:
        logger.error(f"Failed to log audit data: {e}")

    return response