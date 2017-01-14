from flask import jsonify
from flask import Flask
from flask import request
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import twitter
from datetime import datetime, timedelta

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
	city = request.args.get('city')
	meal = request.args.get('meal')
	params = {
		'term': meal
	}

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

@app.route('/twitter')
def retrieveTweets():
	api = twitter.Api(consumer_key= "gMUVzhubG78H2o3HYWFY5csQQ", consumer_secret = "Tc3M4vrraHni2vUWZH9PdeDdUhuHHqbIcpDy9OZjvIICcXgclS", access_token_key = "984138848-PhpKudC6iLRjwLuU1LBbOH5hq4iknM3NoI7jcizL", access_token_secret = "EHazGd0Xgx9LGFVxtKgwC5hVzLns7A8orJphSNn45CqKr")

	query = request.args.get('query')

	sinceDate = datetime.today() - timedelta(days=7)
	since = sinceDate.strftime("%Y-%m-%d")
	results = api.GetSearch(raw_query = 'q=' + query + '&since=' + since + '&count=100')
	tweets = [extract_tweet(tweet) for tweet in results]
	return jsonify(tweets)

def extract_business(business):
	id = business.id
	name = business.name
	rating = business.rating
	image_url = business.image_url
	review_count = business.review_count
	snippet_text = business.snippet_text
	lat = business.location.coordinate.latitude
	long = business.location.coordinate.longitude

	return {'id': id,
			'name': name,
			'rating': rating,
			'image_url': image_url,
			'review_count': review_count,
			'snippet_text': snippet_text,
			'lat': lat,
			'long': long}

def extract_tweet(tweet):
	text = tweet.text
	created_at = tweet.created_at

	return {'text': text,
			'created_at': created_at}

if __name__ == "__main__":
	app.run()
