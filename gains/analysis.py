from collections import namedtuple


Set = namedtuple('Set', ['reps', 'weight'])
_Exercise = namedtuple('Exercise', ['date', 'name', 'sets'])


class Exercise(_Exercise):

    @property
    def weights(self):
        return [s.weight for s in self.sets]

    @property
    def maximum_weight(self):
        return max(self.weights)

    @property
    def average_weight(self):
        return sum(self.weights) / len(self.weights)


class Analysis:

    def __init__(self, exercises):
        self.exercises = exercises
