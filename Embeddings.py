import json
import boto3

from Universal_Variables import *


#to generate the embedding from the text
def generate_text_embeddings(model_id, text):
    input_type = "search_document"
    embedding_types = ["float"]

    body = json.dumps({
        "texts": text,
        "input_type": input_type,
        "embedding_types": embedding_types
    })
    
    accept = '*/*'
    content_type = 'application/json'

    bedrock = boto3.client(service_name=service_name, region_name=region_name)

    response = bedrock.invoke_model(
        body = body,
        modelId = model_id,
        accept = accept,
        contentType = content_type
    )
    
    response_body = json.loads(response.get('body').read())

    return response_body
