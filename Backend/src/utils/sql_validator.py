import re
from typing import List, Optional
from sqlglot import parse_one, exp
from sqlglot.errors import ParseError
from src.utils.config_loader import load_yaml

class SQLValidator:

    def __init__(self):
        config = load_yaml("llm.yaml")["sql_generation"]
        self.allowed_tables = set(config["allowed_tables"])
        self.allowed_columns = set(config["allowed_columns"])
        self.max_rows = config["max_rows"]
        self.require_electricity_id = config["require_where_electricity_id"]
    
    def validate(self, sql: str, electricity_id: Optional[str] = None) -> tuple[bool, str]:
        """Returns (is_valid, error_message)"""
        sql = sql.strip().rstrip(";")
        
        # 1. Basic safety checks
        if not sql.lower().startswith("select"):
            return False, "Only SELECT queries allowed"
        
        if any(kw in sql.lower() for kw in ["insert", "update", "delete", "drop", "alter", "truncate"]):
            return False, "Dangerous keywords detected"
        
        # 2. Parse AST for deeper validation
        try:
            parsed = parse_one(sql, dialect="postgres")
        except ParseError as e:
            return False,f"SQL parse error: {str(e)[:100]}... Try rephrasing your question."
        
        # 3. Check table access
        tables = {table.name.lower() for table in parsed.find_all(exp.Table)}
        if not tables.issubset(self.allowed_tables):
            return False, f"Access denied to tables: {tables - self.allowed_tables}"
        
        # 4. Check columns
        columns = set()
        for col in parsed.find_all(exp.Column):
            columns.add(col.name.lower())
        if not columns.issubset(self.allowed_columns | {"*"}):
            return False, f"Access denied to columns: {columns - self.allowed_columns}"
        
        # 5. electricity_id filter
        if self.require_electricity_id and electricity_id:
            if "electricity_id" not in sql.lower():
                return False, "Query must filter by electricity_id"
            # Check if it's parameterized or properly quoted
            if electricity_id not in sql and f"'{electricity_id}'" not in sql:
                return False, "electricity_id filter must use provided value"
        
        # 6. Limit results
        if "limit" not in sql.lower():
            sql += f" LIMIT {self.max_rows}"
        
        return True, sql



    def parameterize(self, sql: str, params: dict) -> str:
        """Simple parameterization for electricity_id """
        for key, value in params.items():
            # Escape single quotes
            safe_value = str(value).replace("'", "''")
            sql = sql.replace(f":{key}", f"'{safe_value}'")
        return sql



sql_validator = SQLValidator()