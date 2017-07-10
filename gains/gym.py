from collections import namedtuple
from enum import Enum
from itertools import groupby

import plotly.offline as plotly
import plotly.graph_objs as go


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
    glutes = 'glutes'

    shoulders = 'shoulders'

    trapezius = 'trapezius'

    quads = 'quads'
    hamstrings = 'hamstrings'
    calves = 'calves'
    abductors = 'abductors'
    adductors = 'adductors'


class Exercise(_Exercise):

    @property
    def body_weight(self):
        return self.maximum_weight == 0

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

    def chart(self, muscle):
        muscle_exercises = self.exercises(muscle)

        data = []

        keyfunc = lambda e: e.name
        sorted_exercises = sorted(muscle_exercises, key=keyfunc)
        grouped_exercises = groupby(sorted_exercises, keyfunc)

        for name, exercises in grouped_exercises:
            exercises = list(exercises)

            if any(e.body_weight for e in exercises):
                continue

            data.append(
                go.Scatter(
                    x=[e.date for e in exercises],
                    y=[e.average_weight for e in exercises],
                    name=name,
                    mode='lines+markers',
                )
            )

        layout = {
            'yaxis': {'title': 'Weight (kg)'},
        }

        figure = {'data': data, 'layout': layout}

        return plotly.plot(figure, output_type='div')

    @property
    def charts(self):
        return {
            muscle: self.chart(muscle) for muscle in Muscle
        }
