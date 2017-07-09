from collections import namedtuple
from enum import Enum


Set = namedtuple('Set', ['reps', 'weight'])
_Exercise = namedtuple('Exercise', ['date', 'name', 'muscle', 'sets'])


class Muscle(Enum):
    Abs = 'abs'

    Triceps = 'triceps'
    Biceps = 'biceps'
    Forearms = 'forearms'

    Chest = 'chest'

    UpperBack = 'upper back'
    LowerBack = 'lower back'
    Bum = 'bum'

    Shoulders = 'shoulders'

    Trapezius = 'trapezius'

    Quads = 'quads'
    Hamstrings = 'hamstrings'
    Calves = 'calves'
    Abductors = 'abductors'
    Adductors = 'adductors'


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
