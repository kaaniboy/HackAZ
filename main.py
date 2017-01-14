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

@app.route("/activities")
def activities():
	city = request.args.get('city')
	return jsonify(retrieve_activities(city))

def retrieve_activities(city):
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
	EPOCHS = 50
	POPULATION_SIZE = 100
	ELITISM_OFFSET = 10
	MUTATION_OFFSET = 5

	museums = retrieve_activities("Phoenix")
	breakfasts = retrieve_restaurants("Phoenix", "breakfast")
	lunches = retrieve_restaurants("Phoenix", "lunch")
	dinners = retrieve_restaurants("Phoenix", "dinner")

	population = gen_initial_population(POPULATION_SIZE, museums, breakfasts, lunches, dinners)

	for epoch in range(0, EPOCHS):
		total_fitness = calc_total_fitness(population)
		print('Total fitness: (' + str(epoch) + '): ' + str(total_fitness), file=sys.stderr)

		elites = []
		mutants = []
		others = []

		for i in range(0, ELITISM_OFFSET):
			elites.append(roulette_select(population, total_fitness))

		for i in range(0, MUTATION_OFFSET):
			base = roulette_select(population, total_fitness)

			mutant = base.mutate(museums, breakfasts, lunches, dinners)
			while not mutant.isValid():
				mutant = base.mutate(museums, breakfasts, lunches, dinners)

			mutants.append(mutant)

		for i in range(0, POPULATION_SIZE - ELITISM_OFFSET - MUTATION_OFFSET):
			parent1 = roulette_select(population, total_fitness)
			parent2 = roulette_select(population, total_fitness)

			child = parent1.crossover(parent2)
			while not child.isValid():
				child = parent1.crossover(parent2)

			others.append(child)

		population = elites + mutants + others

	sch = find_best_in_population(population)
	print('Best Schedule: ' + str(sch.toJSON()['fitness']), file=sys.stderr)
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
		schedule.afternoon_activities = museums[2:4]

		population.append(schedule)
	return population

def find_best_in_population(population):
	best_fitness = population[0].toJSON()['fitness']
	best = population[0]

	for i in range(1, len(population)):
		curr_fitness = population[i].toJSON()['fitness']
		print('Fitness: ' + str(curr_fitness), file=sys.stderr)


		if curr_fitness > best_fitness:
			best = population[i]
			best_fitness = curr_fitness

	return best

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
