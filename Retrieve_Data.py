from Database_Connect import connection_string
from Universal_Variables import region_name
from Model_Id import embedding_model_id
from Collection import *

from langchain_community.vectorstores import DistanceStrategy
from langchain_postgres.vectorstores import PGVector
from langchain_core.vectorstores import VectorStore
from langchain.retrievers import MergerRetriever
from langchain_aws import BedrockEmbeddings


def search(data):
    capacity = int(data.get('no_of_adults')) + int(data.get('no_of_children'))
    query = data.get('vehicle_type')+" type of car for "+data.get('preference')+" for "+str(data.get('no_of_adults'))+" adults and "+str(data.get('no_of_children'))+" children"
    
    embeddings = BedrockEmbeddings(model_id=embedding_model_id, region_name=region_name)
    
    cars_store = PGVector.from_existing_index(
        embedding=embeddings,
        collection_name='test2_cars',
        distance_strategy=DistanceStrategy.COSINE,
        pre_delete_collection=False,
        connection=connection_string
        )
    
    history_store = PGVector.from_existing_index(
        embedding=embeddings,
        collection_name='test2_history',
        distance_strategy=DistanceStrategy.COSINE,
        pre_delete_collection=False,
        connection=connection_string
        )

    retriever1 = cars_store.as_retriever(
        search_type="similarity", 
        search_kwargs={
            "k": 5, 
            "include_metadata": True
        }
    )

    retriever2 = history_store.as_retriever(
        search_type="similarity", 
        search_kwargs={
            "k": 5, 
            "include_metadata": True
        }
    )

    lotr = MergerRetriever(retrievers=[retriever1, retriever2])
    docs = lotr.invoke(query)
    i = 1

    for doc in docs:
        # Access the document's content
        doc_content = doc.page_content
        # Access the document's metadata object
        doc_metadata = doc.metadata
    
        print("Document no: " + str(i))
        print("Content snippet:" + doc_content)
        print("Document source: " + doc_metadata['source'])
        print("-----")
        i+=1

data = {
    'pickup_location': 'Kolkata',
    'pickup_date': '02-09-2024',
    'pickup_time': 'Morning',
    'drop_off_location': 'Bangalore',
    'drop_off_date': '09-09-2024',
    'drop_off_time': 'Noon',
    'age_verification': '25+',
    'country': 'India',
    'customer_id': 12345,
    'no_of_adults': 4,
    'no_of_children': 0,
    'vehicle_type': 'SUV',
    'preference': 'a long drive on the highway with friends'
}

#search(data)