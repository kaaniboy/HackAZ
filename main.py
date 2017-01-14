from __future__ import print_function
from flask import jsonify
from flask import Flask
from flask import request
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import twitter
import json
import random
import sys
from datetime import datetime, timedelta
from schedule import Schedule

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

	return jsonify(retrieve_restaurants(city, meal))

def retrieve_restaurants(city, meal):
	params = {
		'term': meal
	}

	response = client.search(city, **params)
	data = [extract_business(business) for business in response.businesses]
	return data

@app.route("/museums")
def museums():
	city = request.args.get('city')
	return jsonify(retrieve_museums(city))

def retrieve_museums(city):
	params = {
		'term': 'museum'
	}

	response = client.search(city, **params)
	data = [extract_business(business) for business in response.businesses]
	return data


@app.route('/twitter')
def retrieveTweets():
	api = twitter.Api(consumer_key= "gMUVzhubG78H2o3HYWFY5csQQ", consumer_secret = "Tc3M4vrraHni2vUWZH9PdeDdUhuHHqbIcpDy9OZjvIICcXgclS", access_token_key = "984138848-PhpKudC6iLRjwLuU1LBbOH5hq4iknM3NoI7jcizL", access_token_secret = "EHazGd0Xgx9LGFVxtKgwC5hVzLns7A8orJphSNn45CqKr")

	query = request.args.get('query')

	sinceDate = datetime.today() - timedelta(days=7)
	since = sinceDate.strftime("%Y-%m-%d")
	results = api.GetSearch(raw_query = 'q=' + query + '&since=' + since + '&count=100')
	tweets = [extract_tweet(tweet) for tweet in results]
	return jsonify(tweets)

@app.route('/simulate')
def simulate():
	return jsonify([sch.toJSON() for sch in run_simulation()])
	#return str(len(run_simulation()))

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

def run_simulation():
	EPOCHS = 5
	POPULATION_SIZE = 100
	ELITISM_OFFSET = 10
	MUTATION_OFFSET = 5
	population = []

	museums = retrieve_museums("Phoenix")
	breakfasts = retrieve_restaurants("Phoenix", "breakfast")
	lunches = retrieve_restaurants("Phoenix", "lunch")
	dinners = retrieve_restaurants("Phoenix", "dinner")

	population = gen_initial_population(POPULATION_SIZE, museums, breakfasts, lunches, dinners)

	for epoch in range(0, EPOCHS):
		total_fitness = calc_total_fitness(population)
		print('Total fitness: ' + str(total_fitness), file=sys.stderr)

		elites = []
		mutants = []

		for i in range(0, ELITISM_OFFSET):
			elites.append(roulette_select(population, total_fitness))
		for i in range(0, MUTATION_OFFSET):
			pass
		for i in range(0, POPULATION_SIZE - ELITISM_OFFSET - MUTATION_OFFSET):
			



	sch = roulette_select(population, total_fitness)
	print('Roulette fitness: ' + str(sch.toJSON()['fitness']), file=sys.stderr)
	return population


def gen_initial_population(size, museums, breakfasts, lunches, dinners):
	population = []
	for i in range(0, size):
		schedule = Schedule()
		schedule.breakfast = random.choice(breakfasts)
		schedule.lunch = random.choice(lunches)
		schedule.dinner = random.choice(dinners)

		random.shuffle(museums)
		schedule.morning_activities = museums[:2]
		random.shuffle(museums)
		schedule.afternoon_activities = museums[:2]

		population.append(schedule)
	return population

def calc_total_fitness(population):
	total = 0
	for sch in population:
		total = total + sch.toJSON()['fitness']
	return total

def roulette_select(population, total_fitness):
	rand = random.random()
	i = 0
	for sch in population:
		i = i + (sch.toJSON()['fitness'] / (1.0 * total_fitness))
		if rand <= i:
			return sch
	return None

if __name__ == "__main__":
	app.run()
