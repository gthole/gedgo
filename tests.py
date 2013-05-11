from django.test import TestCase
from gedgo.update import update_from_file
from gedgo.models import Person, Family, Gedcom
from datetime import date

class UpdateGedcom(TestCase):

    def setUp(self):
        self.file_ = 'gedgo/static/test/test.ged'
        update_from_file(None, self.file_, verbose=False)

    def test_person_import(self):
        self.assertEqual(Person.objects.count(), 6)
        p = Person.objects.get(pointer='I1')
        self.assertEqual(p.first_name, "John")
        self.assertEqual(p.last_name, "Doe")
        self.assertEqual(p.birth.place, "Houston, Texas")
        self.assertEqual(p.birth.date,
        				 date(1950, 3, 22))

    def test_family_import(self):
        self.assertEqual(Family.objects.count(), 2)
        f = Family.objects.get(pointer='F1')
        self.assertEqual(
        	list(f.husbands.values_list('pointer')),
        	[('I1',)])
        self.assertTrue(
        	list(f.wives.values_list('pointer')),
        	[('I2',)])
        self.assertTrue(
        	list(f.children.values_list('pointer')),
        	[('I3',), ('I4',)])

    def test_update_from_gedcom(self):
    	g = Gedcom.objects.get()
        update_from_file(g, self.file_, verbose=False)
        self.assertEqual(Person.objects.count(), 6)
        self.assertEqual(Family.objects.count(), 2)
