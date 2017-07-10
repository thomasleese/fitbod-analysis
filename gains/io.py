from collections import namedtuple
import csv
from datetime import datetime
from difflib import SequenceMatcher
from itertools import groupby
import re

from .gym import Analysis, Exercise, Muscle, Set


FitbodExercise = namedtuple(
    'FitbodExercise', ['date', 'name', 'muscle', 'sets', 'reps', 'weight']
)


class FitbodLoader:

    date_format = '%a %b %d %Y %H:%M:%S %Z%z'

    muscles = {
        'Crunch': Muscle.abs,
        'Russian Twist': Muscle.abs,
        'Leg Raise': Muscle.abs,
        'Flutter Kicks': Muscle.abs,
        'Sit-Up': Muscle.abs,
        'Side Bridge': Muscle.abs,
        'Scissor Kick': Muscle.abs,
        'Toe Touchers': Muscle.abs,
        'Pallof Press': Muscle.abs,
        'Cable Wood Chop': Muscle.abs,
        'Scissor Crossover Kick': Muscle.abs,
        'Plank': Muscle.abs,
        'Leg Pull-In': Muscle.abs,
        'Knee Raise': Muscle.abs,
        'Bird Dog': Muscle.abs,
        'Dead Bug': Muscle.abs,
        'Abs': Muscle.abs,

        'Tricep': Muscle.triceps,
        'Bench Dips': Muscle.triceps,
        'bell Curl': Muscle.biceps,
        'Bicep': Muscle.biceps,
        'Preacher Curls': Muscle.biceps,
        'bell Wrist Curl': Muscle.forearms,

        'Cable Crossover Fly': Muscle.chest,
        'Chest': Muscle.chest,
        'Bench Press': Muscle.chest,
        'Machine Fly': Muscle.chest,
        'Push Up': Muscle.chest,
        'Smith Machine Press': Muscle.chest,

        'Pulldown': Muscle.upper_back,
        'Cable Row': Muscle.upper_back,
        'Machine Row': Muscle.upper_back,
        'bell Row': Muscle.upper_back,
        'Pull Up': Muscle.upper_back,
        'Pull-Up': Muscle.upper_back,
        'Pullup': Muscle.upper_back,
        'Chin Up': Muscle.upper_back,
        'Smith Machine Row': Muscle.upper_back,
        'Shotgun Row': Muscle.upper_back,
        'Back Extension': Muscle.lower_back,
        'Superman': Muscle.lower_back,
        'Hip': Muscle.glutes,
        'Step Up': Muscle.glutes,
        'Leg Lift': Muscle.glutes,
        'Glute': Muscle.glutes,
        'Rack Pulls': Muscle.glutes,
        'Pull Through': Muscle.glutes,

        'Shoulder Press': Muscle.shoulders,
        'Lateral': Muscle.shoulders,
        'Face Pull': Muscle.shoulders,
        'Delt Fly': Muscle.shoulders,
        'One-Arm Upright Row': Muscle.shoulders,
        'Dumbbell Raise': Muscle.shoulders,

        'Barbell Shrug': Muscle.trapezius,
        'Neck': Muscle.trapezius,

        'Leg Press': Muscle.quads,
        'Leg Extension': Muscle.quads,
        'Lunge': Muscle.quads,
        'Squat': Muscle.quads,
        'Tuck Jump': Muscle.quads,
        'Mountain Climbers': Muscle.quads,
        'Burpee': Muscle.quads,
        'Leg Curl': Muscle.hamstrings,
        'Deadlift': Muscle.hamstrings,
        'Calf Raise': Muscle.calves,
        'Thigh Abductor': Muscle.abductors,
        'Clam': Muscle.abductors,
        'Thigh Adductor': Muscle.adductors,
    }

    def __init__(self, file):
        if isinstance(file, str):
            with open(file) as f:
                loaded_exercises = self._load_exercises(f)
        else:
            loaded_exercises = self._load_exercises(file)

        self.exercises = self._group_exercises(loaded_exercises)

        self.analysis = Analysis(self.exercises)

    def _parse_date(self, date_string):
        match = re.search(r'^([a-zA-Z0-9\+\:\s]+) \([A-Z]+\)$', date_string)
        date_string = match.group(1)
        return datetime.strptime(date_string, self.date_format)

    def _find_muscle(self, name):
        results = []

        for key, muscle in self.muscles.items():
            if key in name:
                return muscle

        for key, muscle in self.muscles.items():
            matcher = SequenceMatcher(None, key, name)
            ratio = matcher.ratio()
            if ratio >= 0.75:
                results.append((ratio, muscle))

        if not results:
            raise ValueError(f'No matching muscles for: {name}')

        return sorted(results)[0][1]

    def _load_exercises(self, file):
        exercises = []

        reader = csv.reader(file)
        for date, name, sets, reps, weight, warmup, *_ in reader:
            if warmup:
                continue

            date = self._parse_date(date)
            muscle = self._find_muscle(name)

            exercises.append(
                FitbodExercise(
                    date, name, muscle, int(sets), int(reps), float(weight)
                )
            )

        return sorted(exercises, key=lambda row: (row.date, row.name))

    def _group_exercises(self, sorted_exercises):
        exercises = []

        groups = groupby(sorted_exercises,
                         key=lambda row: (row.date, row.name, row.muscle))

        for (date, name, muscle), group_exercises in groups:
            sets = [Set(e.reps, e.weight) for e in group_exercises]
            exercises.append(Exercise(date, name, muscle, sets))

        return exercises


class DictOutput:

    def __init__(self, analysis):
        self.dict = {
            'exercises': [self._exercise(e) for e in analysis.exercises()]
        }

    def _exercise(self, exercise):
        return {
            'date': exercise.date.isoformat(),
            'name': exercise.name,
            'muscle': exercise.muscle.value,
            'sets': [self._set(s) for s in exercise.sets],
        }

    def _set(self, set):
        return {
            'reps': set.reps,
            'weight': set.weight,
        }


class DictInput:

    def __init__(self, data):
        self.analysis = Analysis(self._load_exercises(data['exercises']))

    def _load_exercises(self, data):
        exercises = []

        for record in data:
            exercises.append(
                Exercise(
                    record['date'],
                    record['name'],
                    Muscle(record['muscle']),
                    self._load_sets(record['sets']),
                )
            )

        return exercises

    def _load_sets(self, data):
        return [self._load_set(record) for record in data]

    def _load_set(self, data):
        return Set(data['reps'], data['weight'])
