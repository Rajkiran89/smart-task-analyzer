# from django.test import TestCase

# # Create your tests here.

from django.test import TestCase
from .services import TaskAnalyzer

class TaskAnalyzerTests(TestCase):

    def setUp(self):
        # This runs before every test
        self.basic_tasks = [
            {"id": 1, "title": "A", "due_date": "2025-12-01", "estimated_hours": 5, "importance": 5, "dependencies": []},
            {"id": 2, "title": "B", "due_date": "2025-12-01", "estimated_hours": 5, "importance": 5, "dependencies": []}
        ]

    def test_high_importance_wins(self):
        """Test that a task with Importance 10 beats Importance 1"""
        tasks = [
            {"id": 1, "importance": 10, "due_date": "2025-12-01", "estimated_hours": 5, "dependencies": []},
            {"id": 2, "importance": 1, "due_date": "2025-12-01", "estimated_hours": 5, "dependencies": []}
        ]
        analyzer = TaskAnalyzer(tasks)
        results = analyzer.analyze()
        
        # The first result should be ID 1 (Importance 10)
        self.assertEqual(results[0]['id'], 1)

    def test_past_due_urgency(self):
        """Test that a past-due task gets a massive score boost"""
        tasks = [
            {"id": 1, "title": "Future", "due_date": "2030-01-01", "estimated_hours": 5, "dependencies": []},
            {"id": 2, "title": "Past Due", "due_date": "2020-01-01", "estimated_hours": 5, "dependencies": []}
        ]
        analyzer = TaskAnalyzer(tasks)
        results = analyzer.analyze()
        
        # The overdue task should be first
        self.assertEqual(results[0]['id'], 2)
        # Score should be very high (> 100 based on our math)
        self.assertTrue(results[0]['score'] > 100)

    def test_circular_dependency_detection(self):
        """Test that the algorithm catches Task A waiting for Task B waiting for Task A"""
        tasks = [
            {"id": 1, "dependencies": [2]}, # 1 waits for 2
            {"id": 2, "dependencies": [1]}  # 2 waits for 1 (Cycle!)
        ]
        analyzer = TaskAnalyzer(tasks)
        results = analyzer.analyze()
        
        # Both tasks should be flagged
        for task in results:
            self.assertIn("Circular dependency", task['explanation'])
            self.assertEqual(task['score'], -1)