from flask import Flask, Response, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client
import boto3
from boto3.dynamodb.conditions import Attr, Key
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")

dynamodb = boto3.resource('dynamodb', region_name='us-east-1',aws_access_key_id = aws_access_key, aws_secret_access_key = aws_secret_key)
table = dynamodb.Table('Subscribers')

client = Client(account_sid, auth_token)

base_url = 'https://meme-api.com/gimme'

app = Flask(__name__)
CORS(app)


def getRandomMeme():
    response = requests.get(base_url)
    if response.status_code == 200:
        meme_data = response.json()
        return meme_data
    else:
        print(f"Failed to retreive data {response.status_code}")

def sendMemeOnSignUp(number):
    try:
        meme = getRandomMeme()
        meme_url = meme['url']
        response = client.messages.create( 
            body="Here is your daily meme!",
            from_= twilio_number,
            to=number,
            media_url=[meme_url]
        )
        
    except Exception as e:
        print(f'Could not get meme {e}')
        
    

def sendDailyMeme():
    try:
        response = table.scan(
            FilterExpression=Attr('subscribed').eq(1)
)
        for item in response['Items']:
            number = item['phonenumber']
            meme = getRandomMeme()
            meme_url = meme["url"]

            response = client.messages.create( 
                body="Here is your daily meme!",
                from_= twilio_number,
                to=number,
                media_url=[meme_url]
            )
        
      
    except Exception as e:
        print(f'Could not send meme {e}')
        


@app.route('/submit/<phoneNumber>')
def submit(phoneNumber):
    response = table.get_item(
        Key={'phonenumber': phoneNumber}
    )
    
    try:

        if phoneNumber in response:
            message = f'Number already registered'
            return
        
        else:
            table.put_item(
                Item={
                    'phonenumber': phoneNumber,
                    'subscribed': 1
                }
            )
            message = f"You will now receive daily memes at {phoneNumber}"
            sendMemeOnSignUp(phoneNumber)
    except:
        print('Error')
        
    return {'message': message}

@app.route('/delete/<phonenumber>')
def delete(phonenumber):
    table.delete_item(
    Key={
        'phonenumber': phonenumber
    }
    )
    return {'message': f'deleted {phonenumber}'}


@app.route("/sms", methods=["POST"])
def sms_reply():
    from_number = request.form.get("From")
    normalized_number = from_number.lstrip("+")
    message_body = request.form.get("Body", "").strip().upper()
    response = table.get_item(Key={'phonenumber' : normalized_number})
    item = response.get('Item')
    
    if message_body == 'STOP' and item:
        table.update_item(
            Key={'phonenumber': normalized_number,},
            UpdateExpression='SET subscribed =:val',
            ExpressionAttributeValues={':val': 0}
        )
            
           
        print(f'Unsubcribed {from_number}')
        
    
    elif message_body == 'START' and item:
        table.update_item(
            Key={'phonenumber': normalized_number,},
            UpdateExpression='SET subscribed =:val',
            ExpressionAttributeValues={':val': 1}
        )

        print(f'{from_number} resubscribed')
        
    
    return Response("<Response></Response>", mimetype="text/xml") 


@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
    

    
