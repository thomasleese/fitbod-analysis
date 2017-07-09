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

    date_format = "%a %b %d %Y %H:%M:%S %Z%z"

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
        'abs': Muscle.abs,

        'Tricep': Muscle.triceps,
        'Bench Dips': Muscle.triceps,
        'bell Curl': Muscle.biceps,
        'Bicep': Muscle.biceps,
        'Preacher Curls': Muscle.biceps,
        'bell Wrist Curl': Muscle.forearms,

        'Cable Crossover Fly': Muscle.chest,
        'chest': Muscle.chest,
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
        'Hip': Muscle.bum,
        'Step Up': Muscle.bum,
        'Leg Lift': Muscle.bum,
        'Glute': Muscle.bum,
        'Rack Pulls': Muscle.bum,
        'Pull Through': Muscle.bum,

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

    def __init__(self, filename):
        self.filename = filename
        self.exercises = self._group_exercises(self._load_exercises())
        self.analysis = Analysis(self.exercises)

    def _parse_date(self, date_string):
        match = re.search(r"^([a-zA-Z0-9\+\:\s]+) \([A-Z]+\)$", date_string)
        date_string = match.group(1)
        return datetime.strptime(date_string, self.date_format)

    def _find_muscle(self, name):
        results = []

        for key in self.muscles.keys():
            if key in name:
                return key

        for key in self.muscles.keys():
            matcher = SequenceMatcher(None, key, name)
            ratio = matcher.ratio()
            if ratio >= 0.75:
                results.append((ratio, key))

        if not results:
            raise ValueError(f"No matching muscles for: {name}")

        return sorted(results)[0][1]

    def _load_exercises(self):
        exercises = []

        with open(self.filename) as file:
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
