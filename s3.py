import boto3
import os
 
def test_aws_connection():
    try:
        # Test S3 connection
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        print("Successfully connected to AWS!")
        print("Available S3 buckets:", [bucket['Name'] for bucket in response['Buckets']])
    except Exception as e:
        print(f"Connection failed: {str(e)}")
 
# Test the connection
test_aws_connection()