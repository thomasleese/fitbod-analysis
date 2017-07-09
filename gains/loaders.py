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
        'Crunch': Muscle.Abs,
        'Russian Twist': Muscle.Abs,
        'Leg Raise': Muscle.Abs,
        'Flutter Kicks': Muscle.Abs,
        'Sit-Up': Muscle.Abs,
        'Side Bridge': Muscle.Abs,
        'Scissor Kick': Muscle.Abs,
        'Toe Touchers': Muscle.Abs,
        'Pallof Press': Muscle.Abs,
        'Cable Wood Chop': Muscle.Abs,
        'Scissor Crossover Kick': Muscle.Abs,
        'Plank': Muscle.Abs,
        'Leg Pull-In': Muscle.Abs,
        'Knee Raise': Muscle.Abs,
        'Bird Dog': Muscle.Abs,
        'Dead Bug': Muscle.Abs,
        'Abs': Muscle.Abs,

        'Tricep': Muscle.Triceps,
        'Bench Dips': Muscle.Triceps,
        'bell Curl': Muscle.Biceps,
        'Bicep': Muscle.Biceps,
        'Preacher Curls': Muscle.Biceps,
        'bell Wrist Curl': Muscle.Forearms,

        'Cable Crossover Fly': Muscle.Chest,
        'Chest': Muscle.Chest,
        'Bench Press': Muscle.Chest,
        'Machine Fly': Muscle.Chest,
        'Push Up': Muscle.Chest,
        'Smith Machine Press': Muscle.Chest,

        'Pulldown': Muscle.UpperBack,
        'Cable Row': Muscle.UpperBack,
        'Machine Row': Muscle.UpperBack,
        'bell Row': Muscle.UpperBack,
        'Pull Up': Muscle.UpperBack,
        'Pull-Up': Muscle.UpperBack,
        'Pullup': Muscle.UpperBack,
        'Chin Up': Muscle.UpperBack,
        'Smith Machine Row': Muscle.UpperBack,
        'Shotgun Row': Muscle.UpperBack,
        'Back Extension': Muscle.LowerBack,
        'Superman': Muscle.LowerBack,
        'Hip': Muscle.Bum,
        'Step Up': Muscle.Bum,
        'Leg Lift': Muscle.Bum,
        'Glute': Muscle.Bum,
        'Rack Pulls': Muscle.Bum,
        'Pull Through': Muscle.Bum,

        'Shoulder Press': Muscle.Shoulders,
        'Lateral': Muscle.Shoulders,
        'Face Pull': Muscle.Shoulders,
        'Delt Fly': Muscle.Shoulders,
        'One-Arm Upright Row': Muscle.Shoulders,
        'Dumbbell Raise': Muscle.Shoulders,

        'Barbell Shrug': Muscle.Trapezius,
        'Neck': Muscle.Trapezius,

        'Leg Press': Muscle.Quads,
        'Leg Extension': Muscle.Quads,
        'Lunge': Muscle.Quads,
        'Squat': Muscle.Quads,
        'Tuck Jump': Muscle.Quads,
        'Mountain Climbers': Muscle.Quads,
        'Burpee': Muscle.Quads,
        'Leg Curl': Muscle.Hamstrings,
        'Deadlift': Muscle.Hamstrings,
        'Calf Raise': Muscle.Calves,
        'Thigh Abductor': Muscle.Abductors,
        'Clam': Muscle.Abductors,
        'Thigh Adductor': Muscle.Adductors,
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
