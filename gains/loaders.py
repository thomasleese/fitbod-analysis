from collections import namedtuple
import csv
from datetime import datetime
from itertools import groupby
import re

from .analysis import Analysis, Exercise, Set


FitbodExercise = namedtuple('FitbodExercise',
                            ['date', 'name', 'sets', 'reps', 'weight'])


class FitbodLoader:

    date_format = "%a %b %d %Y %H:%M:%S %Z%z"

    def __init__(self, filename):
        self.filename = filename
        self.exercises = self._group_exercises(self._load_exercises())
        self.analysis = Analysis(self.exercises)

    def _parse_date(self, date_string):
        match = re.search(r"^([a-zA-Z0-9\+\:\s]+) \([A-Z]+\)$", date_string)
        date_string = match.group(1)
        return datetime.strptime(date_string, self.date_format)

    def _load_exercises(self):
        exercises = []

        with open(self.filename) as file:
            reader = csv.reader(file)
            for date, name, sets, reps, weight, warmup, *_ in reader:
                if warmup:
                    continue

                date = self._parse_date(date)

                exercises.append(
                    FitbodExercise(date, name, sets, reps, weight)
                )

        return sorted(exercises, key=lambda row: row.date)

    def _group_exercises(self, sorted_exercises):
        exercises = []

        groups = groupby(sorted_exercises,
                         key=lambda row: (row.date, row.name))

        for (date, name), group_exercises in groups:
            sets = [Set(e.reps, e.weight) for e in group_exercises]
            exercises.append(Exercise(date, name, sets))

        return exercises
