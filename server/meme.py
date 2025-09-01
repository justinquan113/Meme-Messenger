from flask import Flask, Response, request
from flask_cors import CORS
import sqlite3
import requests
import os
import schedule
import time
from dotenv import load_dotenv
from twilio.rest import Client
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

base_url = 'https://meme-api.com/gimme'

app = Flask(__name__)
CORS(app)

connection = sqlite3.connect('store_phoneNumbers.db')

#interact with database
cursor = connection.cursor()

command1 = """CREATE TABLE IF NOT EXISTS
numbers(number INTEGER PRIMARY KEY)"""

cursor.execute(command1)
connection.commit()
connection.close()

def getRandomMeme():
    response = requests.get(base_url)
    if response.status_code == 200:
        meme_data = response.json()
        return meme_data
    else:
        print(f"Failed to retreive data {response.status_code}")

def sendMemeOnSignUp(number):
    try:
        connection = sqlite3.connect('store_phoneNumbers.db')
        cursor = connection.cursor()
        cursor.execute('SELECT number FROM numbers WHERE number = ?', (number,))
        result = cursor.fetchone()
        connection.close()
        
        if result is None:
            print('Number is not DB')
            return
        
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
        connection = sqlite3.connect('store_phoneNumbers.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM numbers')
        result = cursor.fetchall()
        connection.close()
        for row in result:
            number = row[0]
            meme = getRandomMeme()
            meme_url = meme["url"]

            response = client.messages.create( 
                body="Here is your daily meme!",
                from_= twilio_number,
                to=number,
                media_url=[meme_url]
            )
        
      
    except:
        print('Could not send meme')
        


@app.route('/submit/<phoneNumber>')
def submit(phoneNumber):
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO numbers VALUES ({phoneNumber})".format(phoneNumber = phoneNumber))
        connection.commit()
        message = f"You will now receive daily memes at {phoneNumber}"
        sendMemeOnSignUp(phoneNumber)
    except sqlite3.IntegrityError:
        message = f"{phoneNumber} is already registered."
   
    
    finally:
        connection.close()
        
    return {'message': message}



@app.route('/show')
def showNumbers():
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM numbers')
    results = cursor.fetchall()
    connection.close()
    
    return {'registered_numbers' : results}
            


@app.route('/delete/<phoneNumber>', methods=['DELETE'])
def deletePhoneNumber(phoneNumber):
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM numbers WHERE number =?' ,(phoneNumber,))
    connection.commit()
    connection.close()
    message = f"removed {phoneNumber}"
    return {'deleteMessage' : message}


@app.route("/sms", methods=["POST"])
def sms_reply():
    from_number = request.form.get("From")
    message_body = request.form.get("Body")
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    if message_body == 'STOP':
        
        cursor.execute('DELETE FROM numbers WHERE number =?' ,(from_number,))
        connection.commit()
        print(f'Unsubcribed {from_number}')
      
    
    elif message_body == 'START':
        cursor.execute("INSERT INTO numbers (number) VALUES (?)", (from_number,))
        connection.commit()
        print(f"{from_number} resubscribed!")
        
        
    connection.close()
    return Response("<Response></Response>", mimetype="text/xml") 
if __name__ == '__main__':
    app.run(debug=True)
    

    
