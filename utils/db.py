"""
utils/db.py — MySQL connection & schema extraction utilities for QueryWise.
"""

import mysql.connector
from mysql.connector import Error


def connect_to_database(host: str, user: str, password: str, database: str):
    """
    Attempt a MySQL connection. Returns (connection, None) on success,
    or (None, error_message) on failure.
    """
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            connection_timeout=10,
        )
        if conn.is_connected():
            return conn, None
    except Error as e:
        return None, str(e)
    return None, "Unknown connection error."


def get_tables(conn) -> list[str]:
    """Return list of table names in the connected database."""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables


def get_table_row_counts(conn, tables: list[str]) -> dict[str, int]:
    """Return approximate row count for each table."""
    counts = {}
    cursor = conn.cursor()
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            counts[table] = cursor.fetchone()[0]
        except Exception:
            counts[table] = -1
    cursor.close()
    return counts


def extract_table_info(conn, tables: list[str], database_name: str) -> list[str]:
    """
    Extract column definitions and FK relationships for each table.
    Returns a list of human-readable schema strings (one per table).
    """
    cursor = conn.cursor()
    metadata = {}

    for table in tables:
        cursor.execute(f"DESCRIBE `{table}`")
        columns_info = []
        for col in cursor.fetchall():
            columns_info.append({
                "Column": col[0],
                "Type": col[1],
                "Null Constraint": col[2],
                "Key Type": col[3],
                "Default Value": col[4],
                "Extra Constraints": col[5],
            })

        query = """
            SELECT
                TABLE_NAME, COLUMN_NAME,
                CONSTRAINT_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE
                REFERENCED_TABLE_NAME IS NOT NULL
                AND TABLE_NAME = %s
        """
        cursor.execute(query, (table,))
        relationships = cursor.fetchall()
        metadata[table] = {"columns": columns_info, "relationships": relationships}

    cursor.close()

    table_info = []
    for table, info in metadata.items():
        text = f"\nDatabase: {database_name}\n"
        text += f"Table: {table}\n\nColumns:\n"
        for col in info["columns"]:
            text += (
                f"  Column: {col['Column']}, "
                f"Type: {col['Type']}, "
                f"Null: {col['Null Constraint']}, "
                f"Key: {col['Key Type']}, "
                f"Default: {col['Default Value']}, "
                f"Extra: {col['Extra Constraints']}\n"
            )
        if info["relationships"]:
            text += "\nRelationships:\n"
            for row in info["relationships"]:
                text += f"  {row[0]}.{row[1]} → {row[3]}.{row[4]} (constraint: {row[2]})\n"
        else:
            text += "\nRelationships: None\n"
        table_info.append(text)

    return table_info


def preview_table(conn, table: str, limit: int = 5):
    """Return a pandas DataFrame preview of a table."""
    import pandas as pd
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `{table}` LIMIT {limit}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    return pd.DataFrame(rows, columns=columns)


def execute_sql(conn, sql: str):
    """
    Execute a SELECT query and return (DataFrame, None) or (None, error_message).
    """
    import pandas as pd
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        return pd.DataFrame(rows, columns=columns), None
    except Exception as e:
        return None, str(e)
