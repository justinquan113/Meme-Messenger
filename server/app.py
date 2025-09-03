from flask import Flask, Response, request
from flask_cors import CORS
import sqlite3
import requests
import os
import schedule
import time
from dotenv import load_dotenv
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

scheduler = BackgroundScheduler()

base_url = 'https://meme-api.com/gimme'

app = Flask(__name__)
CORS(app)

connection = sqlite3.connect('store_phoneNumbers.db')

#interact with database
cursor = connection.cursor()

command1 = """CREATE TABLE IF NOT EXISTS
users(number TEXT PRIMARY KEY,  subscribed INTEGER DEFAULT 1)"""

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
        cursor.execute('SELECT number FROM users WHERE number = ?', (number,))
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
        cursor.execute('SELECT * FROM users WHERE subscribed = 1')
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
        cursor.execute('INSERT INTO users (number, subscribed) VALUES (?, ?)', (phoneNumber, 1))

        connection.commit()
        message = f"You will now receive daily memes at {phoneNumber}"
        sendMemeOnSignUp(phoneNumber)
    except sqlite3.IntegrityError:
        message = f"{phoneNumber} is already registered."
   
    
    finally:
        connection.close()
        
    return {'message': message}


'''
@app.route('/show')
def showNumbers():
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    results = cursor.fetchall()
    connection.close()
    
    return {'registered_numbers' : results}
            
'''
'''
@app.route('/delete/<phoneNumber>', methods=['DELETE'])
def deletePhoneNumber(phoneNumber):
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM users WHERE number =?' ,(phoneNumber,))
    connection.commit()
    connection.close()
    message = f"removed {phoneNumber}"
    return {'deleteMessage' : message}

'''
@app.route("/sms", methods=["POST"])
def sms_reply():
    from_number = request.form.get("From")
    message_body = request.form.get("Body", "").strip().upper()
    
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    if message_body == 'STOP':
        try:
            cursor.execute('UPDATE users SET subscribed = 0 WHERE number = ?', (from_number,))
            connection.commit()
            print(f'Unsubcribed {from_number}')
        
        except Exception as e:
            print(f'Error {e}')
      
    
    elif message_body == 'START':
        try:
            
            cursor.execute('UPDATE users SET subscribed = 1 WHERE number = ?', (from_number,))
            connection.commit()
            print(f"{from_number} resubscribed!")
            
        except Exception as e:
            print(f'Error {e}')
        
        
    connection.close()
    return Response("<Response></Response>", mimetype="text/xml") 


@scheduler.scheduled_job('cron', hour=10)
def daily_meme():
    sendDailyMeme()

scheduler.start()


@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=False)
    

    
