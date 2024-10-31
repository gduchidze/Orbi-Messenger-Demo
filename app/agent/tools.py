import asyncio

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import create_retriever_tool, tool

from app.messenger import messenger_client
from app.stores.qdrant import qdrant_vectorstore

retriever = qdrant_vectorstore.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_documents",
    "Retrieve project/company related documents",
)


@tool
async def send_contract_sample(config: RunnableConfig):
    """Sends contract samle to user"""
    recipient_id = config["configurable"]["thread_id"]
    asyncio.create_task(messenger_client.send_attachment(recipient_id, attachment_type="file",
                                                         attachment_url="https://docs.google.com/document/d/106UjYKRPM7wtsEeTICwe4UGhw9fTgiQZbBJDrfVfkoo/edit?usp=sharing")
                        )
    return


tools = [retriever_tool, send_contract_sample]
