"""
RAG service — the core question-answering pipeline.
Uses LangChain + Groq to answer questions from retrieved document chunks.
"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.documents import Document
from app.core.config import get_settings
from app.core.logging import logger
from app.models.schemas import ChatMessage, Source
from app.services.vectorstore import similarity_search

settings = get_settings()

SYSTEM_PROMPT = """You are DocuMind, an expert document analyst.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "I couldn't find that in the uploaded documents."
Be concise, accurate, and cite which part of the document your answer comes from.

Context:
{context}"""


def _build_llm() -> ChatGroq:
    """Instantiate the Groq LLM client."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=0.2,          # low temp = more factual, less creative
        max_tokens=1024,
    )


def _format_history(history: list[ChatMessage]) -> list:
    """Convert our schema's ChatMessage list into LangChain message objects."""
    lc_messages = []
    for msg in history:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        else:
            lc_messages.append(AIMessage(content=msg.content))
    return lc_messages


def _build_sources(docs: list[Document]) -> list[Source]:
    """Turn retrieved LangChain Documents into our Source schema."""
    sources = []
    for doc in docs:
        meta = doc.metadata
        sources.append(Source(
            document_id=meta.get("document_id", "unknown"),
            filename=meta.get("filename", meta.get("source", "unknown")),
            excerpt=doc.page_content[:200].strip(),
            page=meta.get("page"),
        ))
    return sources


def answer_question(
    question: str,
    document_id: str | None = None,
    history: list[ChatMessage] = [],
) -> tuple[str, list[Source]]:
    """
    Full RAG pipeline:
      1. Retrieve relevant chunks from ChromaDB
      2. Format context + conversation history
      3. Send to Groq LLM
      4. Return answer + source citations
    """
    # Step 1: Retrieve
    retrieved_docs = similarity_search(question, document_id=document_id)
    if not retrieved_docs:
        return (
            "I couldn't find any relevant content in the uploaded documents.",
            [],
        )

    # Step 2: Build context string from retrieved chunks
    context = "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('filename', 'doc')}]\n{doc.page_content}"
        for doc in retrieved_docs
    )

    # Step 3: Build message list
    system_msg = SystemMessage(content=SYSTEM_PROMPT.format(context=context))
    history_msgs = _format_history(history)
    user_msg = HumanMessage(content=question)

    messages = [system_msg] + history_msgs + [user_msg]

    # Step 4: Call Groq
    llm = _build_llm()
    logger.info(f"Sending query to Groq ({settings.groq_model}): '{question[:60]}...'")
    response = llm.invoke(messages)

    answer = response.content
    sources = _build_sources(retrieved_docs)

    return answer, sources
