from flask import Flask
from flask_cors import CORS
import sqlite3
from twilio.rest import Client
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

@app.route('/submit/<phoneNumber>')
def submit(phoneNumber):
    connection = sqlite3.connect('store_phoneNumbers.db')
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO numbers  VALUES ({phoneNumber})".format(phoneNumber = phoneNumber))
        connection.commit()
        message = f"You will now receive daily memes at {phoneNumber}"
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
    


connection = sqlite3.connect('store_phoneNumbers.db')
cursor = connection.cursor()
cursor.execute('SELECT * FROM numbers')
result = cursor.fetchall()
for row in result:
    number = row[0]
    
connection.close()


if __name__ == '__main__':
    app.run(debug=True)
    
    
    
