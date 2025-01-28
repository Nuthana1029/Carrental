from Database_Connect import connection_string
from Universal_Variables import region_name
from Model_Id import embedding_model_id
from Collection import *
 
from langchain_community.vectorstores import DistanceStrategy
from langchain_community.document_loaders import JSONLoader
from langchain_postgres.vectorstores import PGVector
from langchain_core.vectorstores import VectorStore
from langchain_community.llms import Bedrock
from langchain_aws import BedrockEmbeddings
 
def __main__():
    # Initialize the text embedding model
    embeddings = BedrockEmbeddings(model_id=embedding_model_id, region_name=region_name)
 
    # Create a PGVector instance for the vector database
    store = PGVector(
        collection_name=cars_collection,
        connection=connection_string,
        embeddings=embeddings,
        distance_strategy=DistanceStrategy.COSINE,
        use_jsonb=True
    )
 
    loader = JSONLoader(
        file_path='Cars.json',  #file path to be added
        jq_schema='.',
        text_content=False,
        json_lines=True
    )
 
    data = loader.load()
 
    # Create a PGVector database instance and populate it with vector embeddings
    db = store.from_documents(
        documents=data,
        collection_name=cars_collection,
        connection=connection_string,
        embedding=embeddings,
        distance_strategy=DistanceStrategy.COSINE,
        use_jsonb=True
    )
 
if __name__==__main__():
    __main__()
    print("Complete")