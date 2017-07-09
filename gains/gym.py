from collections import namedtuple
from enum import Enum


Set = namedtuple('Set', ['reps', 'weight'])
_Exercise = namedtuple('Exercise', ['date', 'name', 'muscle', 'sets'])


class Muscle(Enum):
    abs = 'abs'

    triceps = 'triceps'
    biceps = 'biceps'
    forearms = 'forearms'

    chest = 'chest'

    upper_back = 'upper back'
    lower_back = 'lower back'
    bum = 'bum'

    shoulders = 'shoulders'

    trapezius = 'trapezius'

    quads = 'quads'
    hamstrings = 'hamstrings'
    calves = 'calves'
    abductors = 'abductors'
    adductors = 'adductors'


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
        self._exercises = exercises

    def exercises(self, muscle=None):
        results = self._exercises

        if muscle is not None:
            results = [e for e in results if e.muscle == muscle]

        return results
