from langchain_qdrant import QdrantVectorStore
from langchain_voyageai import VoyageAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

from app.config import settings
from app.data.documents import documents

# Initialize Qdrant client and embedding model
client = QdrantClient(url=settings.qdrant_endpoint, api_key=settings.qdrant_api_key)
embedding_model = VoyageAIEmbeddings(model=settings.voyage_default_model, batch_size=32)

# Define collection settings and create if not exists
COLLECTION_NAME = "orbi_collection"
vector_config = VectorParams(size=1024, distance=Distance.COSINE)

if COLLECTION_NAME not in [col.name for col in client.get_collections().collections]:
    client.create_collection(collection_name=COLLECTION_NAME, vectors_config=vector_config)
    qdrant_vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding_model,
    )
    # Add documents only if collection is newly created
    qdrant_vectorstore.add_documents(documents=documents)
else:
    qdrant_vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embedding_model,
    )
