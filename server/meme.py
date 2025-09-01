from flask import Flask
from flask_cors import CORS
from flask import request
import sqlite3
import requests
import os
import schedule
import time
from dotenv import load_dotenv
from vonage import Auth, Vonage
from vonage_messages import MmsImage, MmsResource
load_dotenv()

VONAGE_APP_ID = os.getenv('VONAGE_APP_ID')


client = Vonage(Auth(application_id = VONAGE_APP_ID, private_key = 'private.key'))



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
        response = MmsImage( 
            from_= "16134343047",
            to=number,
            text='Here is yor daily meme!',
            image=MmsResource(url=meme_url),
            
        )
        client.messages.send(response)
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

            response = MmsImage( 
            from_= "16134343047",
            to=number,
            text='Here is yor daily meme!',
            image=MmsResource(url=meme_url),
        )
        client.messages.send(response)
            
    except:
        print('Could not send meme')
        





@app.route('/submit/<phoneNumber>')
def submit(phoneNumber):
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO numbers  VALUES ({phoneNumber})".format(phoneNumber = phoneNumber))
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




if __name__ == '__main__':
    app.run(debug=True)
    

    
