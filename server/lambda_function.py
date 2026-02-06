import requests
import os
from twilio.rest import Client
import boto3
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    # Twilio credentials
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_number = os.environ['TWILIO_PHONE_NUMBER']
    
    # AWS credentials (not needed if using IAM role)
    client = Client(account_sid, auth_token)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Subscribers')
    
    base_url = 'https://meme-api.com/gimme'
    
    try:
        # Get all subscribed users
        response = table.scan(
            FilterExpression=Attr('subscribed').eq(1)
        )
        
        # Send meme to each subscriber
        for item in response['Items']:
            number = item['phonenumber']
            
            # Get random meme
            meme_response = requests.get(base_url)
            if meme_response.status_code == 200:
                meme_data = meme_response.json()
                meme_url = meme_data['url']
                
                # Send via Twilio
                client.messages.create(
                    body="Here is your daily meme!",
                    from_=twilio_number,
                    to=number,
                    media_url=[meme_url]
                )
                print(f"Sent meme to {number}")
            else:
                print(f"Failed to get meme: {meme_response.status_code}")
        
        return {
            'statusCode': 200,
            'body': f'Sent memes to {len(response["Items"])} subscribers'
        }
        
    except Exception as e:
        print(f'Error sending daily memes: {e}')
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }