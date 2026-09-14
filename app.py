import os
import streamlit as st
from dotenv import load_dotenv

from memory_store import load_preferences, save_preferences
from rag_store import initialize_database, ingest_documents, retrieve_chunks
from assistant import answer_question

load_dotenv()

APP_TITLE = "MemoryRAG Assistant"


def render_preferences():
    st.sidebar.header("User preferences")
    current = load_preferences()

    name = st.sidebar.text_input("Preferred name", value=current.get("preferred_name", ""))
    language = st.sidebar.selectbox(
        "Answer language",
        ["English", "Russian", "Finnish"],
        index=["English", "Russian", "Finnish"].index(current.get("answer_language", "English"))
        if current.get("answer_language", "English") in ["English", "Russian", "Finnish"]
        else 0,
    )
    detail = st.sidebar.selectbox(
        "Answer detail",
        ["Short", "Medium", "Detailed"],
        index=["Short", "Medium", "Detailed"].index(current.get("answer_detail", "Medium"))
        if current.get("answer_detail", "Medium") in ["Short", "Medium", "Detailed"]
        else 1,
    )

    if st.sidebar.button("Save preferences"):
        save_preferences(
            {
                "preferred_name": name.strip(),
                "answer_language": language,
                "answer_detail": detail,
            }
        )
        st.sidebar.success("Preferences saved to memory.md")

    return {
        "preferred_name": name.strip(),
        "answer_language": language,
        "answer_detail": detail,
    }


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption("A small assistant with persistent preferences and SQLite-based retrieval-augmented generation.")

    initialize_database()
    ingest_documents()

    preferences = render_preferences()

    st.markdown("### Ask a question about the local document collection")
    question = st.text_input("Question", placeholder="Example: What does the handbook say about remote work?")

    if st.button("Ask"):
        if not question.strip():
            st.warning("Enter a question first.")
            return

        with st.spinner("Searching the document collection..."):
            chunks = retrieve_chunks(question.strip(), top_k=4)

        st.markdown("### Retrieved chunks")
        if not chunks:
            st.info("No relevant document chunks were retrieved.")
        else:
            for i, chunk in enumerate(chunks, start=1):
                with st.expander(f"Chunk {i}: {chunk['source']} (score {chunk['score']:.3f})"):
                    st.write(chunk["text"])

        with st.spinner("Generating grounded answer..."):
            answer = answer_question(question.strip(), chunks, preferences)

        st.markdown("### Answer")
        st.write(answer)

    with st.expander("How grounding works"):
        st.write(
            "The assistant retrieves document chunks from SQLite first. The model is instructed to answer only from those chunks. "
            "If the retrieved text does not contain enough information, it must refuse to invent an answer."
        )


if __name__ == "__main__":
    main()
