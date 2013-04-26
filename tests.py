from django.test import TestCase
from gedgo.models import Event

class TestEvent(TestCase):
    
    def setUp(self):
        self.event = Event(date_approxQ=True, month=1, year_start=1984, place='')
    
    def test_date_string(self):
        """
        Test the date string.
        """
        self.assertEqual(self.event.date_string(), 'January, 1984 (approximate)')
