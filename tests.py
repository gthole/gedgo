from django.test import TestCase
from gedgo.gedcom_update import update
from gedgo.models import Person, Family, Gedcom
from datetime import date


class UpdateGedcom(TestCase):

    def setUp(self):
        self.file_ = 'gedgo/static/test/test.ged'
        update(None, self.file_, verbose=False)

    def test_person_import(self):
        self.assertEqual(Person.objects.count(), 6)

        p = Person.objects.get(pointer='I1')
        self.assertEqual(p.first_name, "John")
        self.assertEqual(p.last_name, "Doe")
        self.assertEqual(p.birth.place, "Houston, Texas")
        self.assertEqual(p.birth.date, date(1950, 3, 22))

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
        update(g, self.file_, verbose=False)
        self.assertEqual(Person.objects.count(), 6)
        self.assertEqual(Family.objects.count(), 2)


class TestViews(TestCase):
    def setUp(self):
        self.file_ = 'gedgo/static/test/test.ged'
        update(None, self.file_, verbose=False)

    def test_pages_load(self):
        pages = [
            '/gedgo/1/',
            '/gedgo/1/I1/'
            '/gedgo/1/F1/'
        ]
        for page in pages:
            print page
            resp = self.client.get(page)
            self.assertEqual(resp.status_code, 200, resp.content)
