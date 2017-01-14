from flask import jsonify
from flask import Flask
from flask import request
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

@app.route("/restaurants")
def restaurants():
    params = {
        'term': 'food'
    }

    city = request.args.get('city')

    response = client.search(city, **params)
    data = [extract_business(business) for business in response.businesses]
    return jsonify(data)

@app.route("/museums")
def museums():
    params = {
        'term': 'museum'
    }

    city = request.args.get('city')

    response = client.search(city, **params)
    data = [extract_business(business) for business in response.businesses]
    return jsonify(data)


def extract_business(business):
    id = business.id
    name = business.name
    rating = business.rating
    image_url = business.image_url
    review_count = business.review_count
    snippet_text = business.snippet_text

    return {'id': id,
            'name': name,
            'rating': rating,
            'image_url': image_url,
            'review_count': review_count,
            'snippet_text': snippet_text}

if __name__ == "__main__":
    app.run()
