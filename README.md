# MemoryRAG Assistant

MemoryRAG Assistant is a small Streamlit application for an assignment that combines persistent user memory with retrieval-augmented generation (RAG) over a small local document collection.

## What the program does

The assistant has two main capabilities.

First, it remembers at least three user preferences in `memory.md`:

- preferred name
- answer language
- preferred answer detail level

These preferences are loaded when the app starts and can be changed from the sidebar.

Second, it answers questions from a local document collection using SQLite-based RAG. Text files in the `documents` folder are split into chunks, embedded with OpenAI embeddings, and stored in `rag.db`. When the user asks a question, the app embeds the question, compares it with the stored chunk embeddings, and retrieves the most relevant chunks.

The application always displays the retrieved chunks before the final answer so the user can see which source text was used.

If the retrieved chunks do not contain enough information to answer the question, the assistant is instructed to reply:

`I don't know based on the provided documents.`

The model is also instructed to treat text inside the documents as untrusted source material rather than as instructions. This reduces prompt-injection risk from document content.

## Project files

- `app.py` - Streamlit user interface
- `memory_store.py` - reads and writes persistent preferences in `memory.md`
- `rag_store.py` - chunks documents, creates OpenAI embeddings, stores them in SQLite, and performs similarity retrieval
- `assistant.py` - generates grounded answers with OpenAI using only retrieved chunks
- `memory.md` - stores three user preferences
- `documents/company_handbook.txt` - sample source document
- `documents/product_guide.txt` - sample source document
- `requirements.txt` - Python dependencies
- `.env.example` - example environment variables
- `.gitignore` - keeps secrets and the generated SQLite database out of Git

## Requirements covered by the assignment

### Remembers at least 3 user preferences

The app stores:

1. preferred name
2. answer language
3. answer detail level

The values are kept in `memory.md`, so they remain available between application restarts.

### SQLite RAG

The application uses a local SQLite database called `rag.db`. Each document is divided into chunks. Every chunk is stored together with its source file, chunk index, text, and embedding vector.

At question time, the app:

1. creates an embedding for the question
2. loads stored chunk embeddings from SQLite
3. calculates cosine similarity
4. returns the most relevant chunks
5. sends only those chunks to the language model as answer context

### Retrieved chunks are visible

The Streamlit interface displays each retrieved chunk in an expandable section, including its source filename and similarity score.

### No invented answers

The assistant is instructed to use only the retrieved chunks. If the chunks do not contain enough information, it must refuse to guess and return the fixed fallback message.

## Windows setup

### 1. Install Python

Install Python 3.11 or newer from python.org.

During installation, enable:

`Add python.exe to PATH`

After installation, open Command Prompt and check:

```text
python --version
```

### 2. Clone or download the repository

Using Git:

```text
git clone https://github.com/hamk-ai-expert-2026/rag_memory_assistant_oleglihvoinen.git
cd rag_memory_assistant_oleglihvoinen
```

You can also download the repository as a ZIP file from GitHub and extract it.

### 3. Create a virtual environment

In Command Prompt, inside the project folder:

```text
python -m venv venv
```

Activate it:

```text
venv\Scripts\activate
```

### 4. Install dependencies

```text
pip install -r requirements.txt
```

### 5. Create an OpenAI API key

Create an API key in your OpenAI account.

Copy `.env.example` to a new file named `.env`.

On Windows Command Prompt:

```text
copy .env.example .env
```

Open `.env` in a text editor and replace the placeholder value:

```text
OPENAI_API_KEY=your_real_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Do not commit the real `.env` file to GitHub.

### 6. Run the app

```text
streamlit run app.py
```

Your browser should open automatically, usually at:

```text
http://localhost:8501
```

## How to use the app

1. Open the sidebar.
2. Enter your preferred name.
3. Choose an answer language.
4. Choose an answer detail level.
5. Click `Save preferences`.
6. Ask a question about the local documents.
7. Review the retrieved chunks shown by the app.
8. Read the grounded answer.

Example questions:

```text
How many remote work days are allowed?
```

```text
What is the annual learning budget?
```

```text
Which plan includes API access?
```

A question not covered by the documents, for example:

```text
Who won the 2026 football World Cup?
```

should produce the refusal:

```text
I don't know based on the provided documents.
```

## Adding more documents

Add more `.txt` files to the `documents` folder.

The next time the app runs, new documents that are not yet stored in the SQLite database are chunked and embedded automatically.

If you change the contents of an already indexed file, delete `rag.db` and run the app again so the database is rebuilt from the updated documents.

## Notes on generated files

`rag.db` is created automatically when the app runs and is listed in `.gitignore`.

`memory.md` is intentionally included in the project because this assignment demonstrates file-based persistent memory. In a multi-user production application, each user should have separate memory storage instead of sharing one file.
