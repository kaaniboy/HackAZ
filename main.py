from __future__ import print_function
from flask import jsonify
from flask import Flask
from flask import request
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import twitter
import json
import random
import os
import sys
import requests
from datetime import datetime, timedelta
from schedule import Schedule

auth = Oauth1Authenticator(
	consumer_key="niAZAbxG4R-zMR_BXSXCSg",
	consumer_secret="QLjZH_19u9unIyfQTK5-k18slzQ",
	token="s8ipQMaCxLziSJcVMbB1Nj20YYijfLpa",
	token_secret="3qsdQR53xxyQtUQMimHrXRvK2e0"
)

LAT = 40.730610
LONG = -73.935242

client = Client(auth)

app = Flask(__name__)

@app.route("/")
def index():
	return "Index"

@app.route("/restaurants")
def restaurants():
	latitude = request.args.get('lat')
	longitude = request.args.get('long')
	meal = request.args.get('meal')

	return jsonify(retrieve_restaurants(latitude, longitude, meal))

def retrieve_restaurants(latitude, longitude, meal):
	params = {
		'term': meal
	}

	response = client.search_by_coordinates(latitude, longitude, **params)
	data = [extract_business(business, "restaurant") for business in response.businesses]
	return data

@app.route("/activities")
def activities():
	latitude = request.args.get('lat')
	longitude = request.args.get('long')
	terms = request.args.get('terms').split(',')
	return jsonify(retrieve_activities(latitude, longitude, terms))

def retrieve_activities(latitude, longitude, terms):
	complete_data = []
	for term in terms:
		params = {
			'term': term
		}

		response = client.search_by_coordinates(latitude, longitude, **params)
		data = [extract_business(business, term) for business in response.businesses]
		complete_data = complete_data + data

	complete_data = complete_data + retrieve_amadeus(latitude, longitude, '50')

	return complete_data

@app.route('/amadeus')
def amadeus():
	latitude = request.args.get("lat")
	longitude = request.args.get("long")
	radius = request.args.get("radius")

	return jsonify(retrieve_amadeus(latitude, longitude, radius))

def retrieve_amadeus(latitude, longitude, radius):
	apikey = "JDe6GYa6Xf1WvmCcRJs39xHPL905xbOi"

	query = "https://api.sandbox.amadeus.com/v1.2/points-of-interest/yapq-search-circle?"
	query += "apikey=" + apikey

	if (latitude != None and longitude != None and radius != None):
		query += "&latitude=" + str(latitude) + "&longitude=" + str(longitude) + "&radius=" + str(radius)

	query += "&social_media=true"

	r = requests.get(query)
	return parseAmadeusJSONIntoObject(r.text)

def parseAmadeusJSONIntoObject(jsonString):
	data = json.loads(jsonString)
	try:
		pointsOfInterest = data["points_of_interest"]
	except:
		return "[]"

	points = []

	for i in range (0, len(pointsOfInterest)):
		singleData = {}

		try:
			name = data["points_of_interest"][i]["title"]

			singleData["id"] = None
			singleData["type"] = "amadeus"
			singleData["name"] = name
			singleData["image_list"] = data["points_of_interest"][i]["main_image"]
			singleData["description"]= data["points_of_interest"][i]["details"]["short_description"]
			singleData["date"] = None
			singleData["TimeTBD"] = None
			singleData["rating"] = data["points_of_interest"][i]["grades"]["yapq_grade"]
			singleData["rating_count"] = None
			singleData["genre"] = None
			#singleData["price"] = None
			singleData["latitude"] = data["points_of_interest"][i]["location"]["latitude"]
			singleData["longitude"] = data["points_of_interest"][i]["location"]["longitude"]
			#singleData["twitter"] = twitterRequest(removeInvalidCharacters(name))
			singleData["link"] = data["points_of_interest"][i]["details"]["wiki_page_link"]

			points.append(singleData)
		except:
			print("FAIL: " + str(singleData), file=sys.stderr)

	totalData = {}
	totalData = points
	return totalData

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
	best = run_simulation()
	return jsonify(best.toJSON())
	#return jsonify([sch.toJSON() for sch in run_simulation()])
	#return str(len(run_simulation()))

def extract_business(business, attraction_type):
	id = business.id
	type = attraction_type
	name = business.name
	image_list = business.image_url
	description = business.snippet_text
	date = None
	time = None
	timeTBD = None
	rating = business.rating
	rating_count = business.review_count
	genre = business.categories
	#price = ...
	latitude = business.location.coordinate.latitude
	longitude = business.location.coordinate.longitude
	#twitter = twitterRequest(removeInvalidCharacters(name))
	link = business.url

	return {'id': id,
			'type' : type,
			'name': name,
			'image_list': image_list,
			'description': description,
			'date' : date,
			'time' : time,
			'timeTBD' : timeTBD,
			'rating': rating,
			'rating_count': rating_count,
			'genre' : genre,
			'latitude': latitude,
			'longitude': longitude,
			'link' : link}

def extract_tweet(tweet):
	text = tweet.text
	created_at = tweet.created_at

	return {'text': text,
			'created_at': created_at}

def run_simulation():
	EPOCHS = os.environ.get("EPOCHS", 50)
	POPULATION_SIZE = os.environ.get("POPULATION_SIZE", 100)
	ELITISM_OFFSET = 10
	MUTATION_OFFSET = 5
	print("Running GE with " + str(EPOCHS) + " epochs and population of " + str(POPULATION_SIZE), file=sys.stderr)
	print("====================================================", file=sys.stderr)

	museums = retrieve_activities(LAT, LONG, ["museum"])
	breakfasts = retrieve_restaurants(LAT, LONG, "breakfast")
	lunches = retrieve_restaurants(LAT, LONG, "lunch")
	dinners = retrieve_restaurants(LAT, LONG, "dinner")

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
	return sch
	#return population


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
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
