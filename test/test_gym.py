from datetime import datetime
from unittest import TestCase

from gains.gym import Analysis, Exercise, Muscle


class TestAnalysis(TestCase):

    exercises = [
        Exercise(datetime.now(), 'Abs', Muscle.abs, []),
        Exercise(datetime.now(), 'Triceps', Muscle.triceps, []),
    ]

    def setUp(self):
        self.analysis = Analysis(self.exercises)

    def test_by_muscle(self):
        exercises = self.analysis.exercises(muscle=Muscle.abs)
        self.assertEqual(len(exercises), 1)

        exercises = self.analysis.exercises(muscle=Muscle.triceps)
        self.assertEqual(len(exercises), 1)
