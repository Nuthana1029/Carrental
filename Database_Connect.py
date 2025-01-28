import json
import boto3
import psycopg
import psycopg2

from urllib.parse import quote_plus
from botocore.exceptions import ClientError

from Universal_Variables import *

secret_name = "rds!db-7a18b7b9-0ae8-4955-a46d-33def5d7059b"

session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

try:
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
except ClientError as e:
    raise e

secret = get_secret_value_response['SecretString']
secrets_dict = json.loads(get_secret_value_response['SecretString'])

bedrock = boto3.client(service_name=service_name, region_name=region_name)
conn = psycopg2.connect(
    host='database-2.ctk2ke8se56b.us-west-2.rds.amazonaws.com',
    port='5432',
    user=secrets_dict['username'],
    password=secrets_dict['password'],
    database='postgres'
)

#to check the postgres connection password when it gets changed
#print(secrets_dict['password'])

#for psycopg3 - to connect with langchain
connection_string=f"postgresql+psycopg://{secrets_dict['username']}:{quote_plus(secrets_dict['password'])}@database-2.ctk2ke8se56b.us-west-2.rds.amazonaws.com:5432/postgres"