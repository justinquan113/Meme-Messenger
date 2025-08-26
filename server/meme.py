from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/submit/<phoneNumber>')
def submit(phoneNumber):
   
    return {'message': f"You will now receive daily memes at {phoneNumber}"}


if __name__ == '__main__':
    app.run(debug=True)