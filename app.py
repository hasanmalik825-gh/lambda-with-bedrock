import boto3
import botocore.config
import json
from datetime import datetime

def content_generation_using_bedrock(content_topic: str) -> str:
    prompt = f"""Human: Write a 50 words content on the topic {content_topic}
    Assistant:"""
    
    body = {
        "prompt": prompt,
        "max_gen_len": 50,
        "temperature": 0.5,
        "top_p": 0.9
    }
    
    try:
        bedrock_client = boto3.client(
            "bedrock-runtime",
            config=botocore.config.Config(
                read_timeout=120,
                connect_timeout=120,
                retries={'max_attempts': 3})
            )
        
        response = bedrock_client.invoke_model(
            body=json.dumps(body),
            modelId="us.meta.llama3-1-8b-instruct-v1:0"
        )
        
        response_content = json.loads(response.get('body').read().decode('utf-8'))
        blog_details = response_content.get('generation', '')
        return blog_details
        
    except Exception as e:
        print(f"Error generating the blog: {e}")
        raise  # Re-raise the exception to trigger error handling

def save_content_s3(s3_key: str, s3_bucket: str, generate_content: str) -> None:
    try:
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=generate_content.encode('utf-8')  # Properly encode content
        )
        print("Content saved to s3")
    except Exception as e:
        print(f"Error when saving the content to s3: {e}")
        raise  # Re-raise the exception to trigger error handling

def lambda_handler(event, context):
    try:
        # Parse the event body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        content_topic = body.get('content_topic')
        if not content_topic:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'content_topic is required'})
            }

        generated_content = content_generation_using_bedrock(content_topic=content_topic)

        if generated_content:
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')  # Updated timestamp format
            s3_key = f"content-output/{current_time}.txt"
            s3_bucket = 'bedrock-content-saver-bucket'
            save_content_s3(s3_key, s3_bucket, generated_content)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Content Generation is completed',
                    'generated_content': generated_content,
                    's3_location': f"s3://{s3_bucket}/{s3_key}"
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'No content was generated'})
            }
            
    except Exception as e:
        print(f"Lambda execution error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }