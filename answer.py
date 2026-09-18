from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from pathlib import Path

llm = ChatOllama(model="gpt-oss:20b", temperature=0)
EMBEDDING_MODEL = 'qwen3-embedding:0.6b'
COLLECTION_NAME = 'google_drive'
DB_NAME = "./chroma_db"
BASE_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / DB_NAME


def get_vector_store():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "The Chroma database does not exist. Run ingest.py first."
        )

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_PATH),
        embedding_function=embeddings,
    )

    return vector_store

def answer_question(question: str):
    vector_store = get_vector_store()
    retrieved = vector_store.similarity_search(question, k=10)

    context_parts = []

    for number, document in enumerate(retrieved, start=1):
        file_name = document.metadata.get("file_name", "Unknown file")
        context_parts.append(
            f"[Source {number}: {file_name}]\n{document.page_content}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
        Answer the question using only the provided sources.
        
        If the sources do not contain enough information, say that the answer was not
        found in the indexed files. Cite supporting sources using [Source 1],
        [Source 2], and so on.
        
        SOURCES:
        {context}
        
        QUESTION:
        {question}
        """

    response = llm.invoke(prompt)
    return response.content, retrieved


# print(answer_question('Based on this documentation you have available, what is the name of the person who owns this data?'))
# print(answer_question('Why was this person made redundant from their job?'))



vector_store = get_vector_store()
stored = vector_store.get()
question = 'Why was this person made redundant from their job?'

retrieved = vector_store.similarity_search(
    question,
    k=10,
)

for number, document in enumerate(retrieved, start=1):
    print(f"RESULT {number}")
    print(document.metadata)
    print(document.page_content)
    print()

# vector_store = get_vector_store()
# stored = vector_store.get()

# matching_chunks = [
#     text
#     for text in stored["documents"]
#     if text and "Elena Marin" in text
# ]
#
# print(f"Matching stored chunks: {len(matching_chunks)}")
#
# for chunk in matching_chunks:
#     print(chunk)
#     print()


# question = "Who is the CEO of BluePeak Hotels?"
#
# retrieved = vector_store.similarity_search(
#     question,
#     k=10,
# )
#
# for number, document in enumerate(retrieved, start=1):
#     print(f"RESULT {number}")
#     print(document.metadata)
#     print(document.page_content)
#     print()