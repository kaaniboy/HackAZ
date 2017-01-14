from flask import jsonify
from flask import Flask
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

auth = Oauth1Authenticator(
    consumer_key="niAZAbxG4R-zMR_BXSXCSg",
    consumer_secret="QLjZH_19u9unIyfQTK5-k18slzQ",
    token="s8ipQMaCxLziSJcVMbB1Nj20YYijfLpa",
    token_secret="3qsdQR53xxyQtUQMimHrXRvK2e0"
)

client = Client(auth)

app = Flask(__name__)

@app.route("/")
def hello():
    params = {
        'term': 'food',
        'lang': 'fr'
    }

    response = client.search('San Francisco', **params)
    data = [business.name for business in response.businesses]
    return jsonify(data)

if __name__ == "__main__":
    app.run()
