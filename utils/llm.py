"""
utils/llm.py — LLM initialisation and SQL/chat generation for QueryWise.
"""

import sqlparse
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

LLM_MODEL = "llama-3.3-70b-versatile"

SQL_PROMPT = PromptTemplate.from_template(
    """
You are QueryWise — an expert MySQL SQL Assistant embedded in a professional analytics platform.
Your task is to generate optimized, production-ready SQL queries.

Rules:
- Only generate SELECT queries
- Never generate DELETE, UPDATE, INSERT, DROP, ALTER, or TRUNCATE queries
- Use explicit column names instead of SELECT *
- Use ONLY the tables and columns provided in the schema context below
- Do not hallucinate tables or columns
- Generate syntactically correct MySQL queries
- Prefer optimized JOINs and filtering
- If the query cannot be generated from the schema, briefly explain why

Return ONLY the raw SQL query. No markdown, no backticks, no explanations before or after.
If you must explain (e.g. the query is impossible), start with "-- Note:" on the first line.

Database Schema Context:
{extracted_content}

User Question:
{user_question}
"""
)

CHAT_PROMPT = PromptTemplate.from_template(
    """
You are QueryWise — a friendly, expert database assistant.
The user may ask general questions about the database, request SQL, ask for explanations of results,
or ask follow-up questions.

Respond helpfully and concisely. If SQL is needed, wrap it in triple backticks with the `sql` language tag.

Database Schema Context:
{extracted_content}

Conversation History:
{history}

User:
{user_question}
"""
)


def get_llm(api_key: str) -> ChatGroq:
    return ChatGroq(
        temperature=0,
        api_key=api_key,
        model=LLM_MODEL,
        max_tokens=3000,
    )


def generate_sql(llm: ChatGroq, user_question: str, context: str) -> tuple[str, str]:
    """
    Generate and format a SQL query.
    Returns (raw_response, formatted_sql).
    """
    chain = SQL_PROMPT | llm
    response = chain.invoke({"user_question": user_question, "extracted_content": context})
    raw = response.content.strip()

    # If LLM returned a note rather than SQL, skip formatting
    if raw.startswith("--") or not any(kw in raw.upper() for kw in ("SELECT", "WITH")):
        return raw, raw

    formatted = sqlparse.format(raw, reindent=True, keyword_case="upper")
    return raw, formatted


def generate_chat_response(llm: ChatGroq, user_question: str, context: str, history: str) -> str:
    """Generate a conversational response that may include SQL."""
    chain = CHAT_PROMPT | llm
    response = chain.invoke({
        "user_question": user_question,
        "extracted_content": context,
        "history": history or "None",
    })
    return response.content.strip()
