from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from config.config import Config

def get_vector_store():
    return Chroma(
        persist_directory = Config.VECTOR_STORE_PATH,
        embedding_function = OpenAIEmbeddings(api_key = Config.OPENAI_API_KEY)
    )
