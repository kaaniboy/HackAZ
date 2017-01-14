import math
class Schedule:
    def __init__(self):
        self.breakfast = None
        self.lunch = None
        self.dinner = None

        self.morning_activities = None
        self.afternoon_activities = None

    def toJSON(self):
        res = {
            'breakfast': self.breakfast,
            'lunch': self.lunch,
            'dinner': self.dinner,
            'morning_activities': self.morning_activities,
            'afternoon_activities': self.afternoon_activities
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

        return dist_error

    def rating_error(self):
        rating_error = 5 - self.breakfast.rating
        rating_error = rating_error + (5 - self.lunch.rating)
        rating_error = rating_error + (5 - self.dinner.rating)

        for i in range(0, len(self.morning_activities)):
            rating_error = rating_error + (5 - self.morning_activities[i].rating)
        for i in range(0, len(self.afternoon_activities)):
            rating_error = rating_error + (5 - self.afternoon_activities[i].rating)

        return rating_error


    def crossover(self, other):
        pass


def dist(first, second):
    return math.sqrt((first.lat - second.lat) ** 2 + (first.long - second.long) ** 2)
