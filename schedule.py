import math
import random

class Schedule:
    def __init__(self):
        self.DIST_WEIGHT = .1
        self.RATING_WEIGHT = .1

        self.breakfast = None
        self.lunch = None
        self.dinner = None

        self.morning_activities = []
        self.afternoon_activities = []

    def toJSON(self):
        res = {
            'breakfast': self.breakfast,
            'lunch': self.lunch,
            'dinner': self.dinner,
            'morning_activities': self.morning_activities,
            'afternoon_activities': self.afternoon_activities,
            'dist_error': self.dist_error(),
            'rating_error': self.rating_error(),
            'total_error': self.error(),
            'fitness': 100 * (1.0 / self.error())
        }

        return res

    #We will attempt to minimize this value.
    def error(self):
        dist = self.dist_error()
        rating = self.rating_error()

        return dist + rating

    def dist_error(self):
        dist_error = dist(self.breakfast, self.morning_activities[0])

        for i in range(1, len(self.morning_activities)):
            dist_error = dist_error + dist(self.morning_activities[i - 1], self.morning_activities[i])

        dist_error = dist_error + dist(self.morning_activities[-1], self.lunch)
        dist_error = dist_error + dist(self.lunch, self.afternoon_activities[0])

        for i in range(1, len(self.afternoon_activities)):
            dist_error = dist_error + dist(self.afternoon_activities[i - 1], self.afternoon_activities[i])

        dist_error = dist_error + dist(self.afternoon_activities[-1], self.dinner)

        return dist_error * self.DIST_WEIGHT

    def rating_error(self):
        rating_error = 5 - self.breakfast['rating']
        rating_error = rating_error + (5 - self.lunch['rating'])
        rating_error = rating_error + (5 - self.dinner['rating'])

        for i in range(0, len(self.morning_activities)):
            rating_error = rating_error + (5 - self.morning_activities[i]['rating'])
        for i in range(0, len(self.afternoon_activities)):
            rating_error = rating_error + (5 - self.afternoon_activities[i]['rating'])

        return rating_error * self.RATING_WEIGHT


    def crossover(self, other):
        child = Schedule()
        for i in range(0, len(self.morning_activities)):
            if random.random() < 0.5:
                child.morning_activities.append(self.morning_activities[i])
            else:
                child.morning_activities.append(other.morning_activities[i])

        for i in range(0, len(self.afternoon_activities)):
            if random.random() < 0.5:
                child.afternoon_activities.append(self.afternoon_activities[i])
            else:
                child.afternoon_activities.append(other.afternoon_activities[i])

        if random.random() < 0.5:
            child.breakfast = self.breakfast
        else:
            child.breakfast = other.breakfast

        if random.random() < 0.5:
            child.lunch = self.lunch
        else:
            child.lunch = other.lunch

        if random.random() < 0.5:
            child.dinner = self.dinner
        else:
            child.dinner = other.dinner

        return child

    def mutate(self, museums, breakfasts, lunches, dinners):
        MUTATION_RATE = 0.20
        child = Schedule()

        if random.random() < MUTATION_RATE:
            child.breakfast = random.choice(breakfasts)
        else:
            child.breakfast = self.breakfast

        if random.random() < MUTATION_RATE:
            child.lunch = random.choice(lunches)
        else:
            child.lunch = self.lunch

        if random.random() < MUTATION_RATE:
            child.dinner = random.choice(dinners)
        else:
            child.dinner = self.dinner

        random.shuffle(museums)
        for i in range(0, len(self.morning_activities)):
            if random.random() < MUTATION_RATE:
                child.morning_activities.append(museums[i])
            else:
                child.morning_activities.append(self.morning_activities[i])

        random.shuffle(museums)
        for i in range(0, len(self.afternoon_activities)):
            if random.random() < MUTATION_RATE:
                child.afternoon_activities.append(museums[i])
            else:
                child.afternoon_activities.append(self.afternoon_activities[i])

        return child

    def isValid(self):
        if self.morning_activities[0] == self.morning_activities[1]:
            return False
        if self.afternoon_activities[0] == self.afternoon_activities[1]:
            return False
        if self.breakfast == self.lunch or self.lunch == self.dinner or self.breakfast == self.dinner:
            return False
        for activity in self.morning_activities:
            if activity in self.afternoon_activities:
                return False
        return True

def dist(first, second):
    return math.sqrt((first['latitude'] - second['latitude']) ** 2 + (first['longitude'] - second['longitude']) ** 2)
