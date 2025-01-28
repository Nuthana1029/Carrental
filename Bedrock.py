import boto3

from Model_Id import llm_model_id
from Universal_Variables import *
 
 
def get_recommendation(prompt, content):
    #model_id = 'anthropic.claude-3-haiku-20240307-v1:0'  # haiku model
    bedrock = boto3.client(service_name=service_name, region_name=region_name)
    message = {"role": "user", "content": [{"text": content}, {"text": prompt}]}
    messages = [message]
    inference_config = {"temperature": 0 , "topP": 0.9, "maxTokens": 4000}  # temperature, topP and token size can be changed
    try:
        response = bedrock.converse(
            modelId=llm_model_id,
            messages=messages,
            inferenceConfig=inference_config
        )
        return response
    except Exception as e:
        return None