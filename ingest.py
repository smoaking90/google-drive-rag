from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from pathlib import Path


EMBEDDING_MODEL = 'qwen3-embedding:0.6b'
# COLLECTION_NAME = 'google_drive'
COLLECTION_NAME = 'test_data'
DB_NAME = "./chroma_db"
BASE_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / DB_NAME



### GETTING DOCUMENTS
def fetch_documents():
    """LangChain loader"""
    file_paths = sorted(TEST_DATA_DIR.rglob("*.md"))
    documents = []
    for file_path in file_paths:
        text = file_path.read_text(encoding="utf-8")
        document = Document(
            page_content=text,
            metadata={
                'source': str(file_path),
                'file_name': file_path.name,
                'file_type': file_path.suffix
            },
        )
        documents.append(document)
    print(f"Loaded {len(documents)} documents")
    return documents


### CREATING CHUNKs
def create_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Divided into {len(chunks)} chunks")
    return chunks



# TO DB
def create_embeddings(chunks):
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if DB_PATH.exists():
        Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(DB_PATH),
            embedding_function=embeddings
        ).delete_collection()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DB_NAME,
    )

    vector_store.add_documents(chunks)

    print(f"Added {len(chunks)} chunks to Chroma")

    return vector_store


if __name__ == "__main__":
    documents = fetch_documents()
    chunks = create_chunks(documents)
    create_embeddings(chunks)
    print("Ingestion complete")