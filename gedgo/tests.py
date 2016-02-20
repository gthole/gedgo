from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User
from django.test.utils import override_settings

from gedgo.gedcom_update import update
from gedgo.models import Person, Family, Gedcom
from datetime import date
from mock import patch


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
        self.gedcom = Gedcom.objects.get()

    def login_user(self, set_super=False):
        u = User.objects.create_user(
            'test',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='foobarbaz'
        )
        self.client.login(username='test', password='foobarbaz')
        u.is_superuser = set_super
        u.save()

    def test_requires_login(self):
        pages = [
            '/gedgo/%s/' % self.gedcom.id,
            '/gedgo/%s/I1/' % self.gedcom.id
        ]
        for page in pages:
            resp = self.client.get(page, follow=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(
                resp.redirect_chain,
                [('/accounts/login/?next=%s' % page, 302)]
            )

    def test_pages_load(self):
        pages = [
            '/gedgo/%s/' % self.gedcom.id,
            '/gedgo/%s/I1/' % self.gedcom.id,
            '/gedgo/dashboard/'
        ]
        self.login_user(set_super=True)
        for page in pages:
            resp = self.client.get(page)
            self.assertEqual(resp.status_code, 200,
                             '%s %s' % (resp.status_code, page))

    def test_comments(self):
        pages = [
            ('/gedgo/1/', 'Test Gedcom'),
            ('/gedgo/1/I1/', 'John Doe (I1)')
        ]
        self.login_user()
        data = {
            'message': 'My test message'
        }
        for page, noun in pages:
            resp = self.client.post(page, data)
            self.assertEqual(resp.status_code, 302)

            self.assertEqual(len(mail.outbox), 1)
            message = mail.outbox[0]
            self.assertEqual(
                message.subject,
                'Comment from Test User about %s' % noun
            )
            self.assertEqual(message.body, data['message'] + '\n\n')

            mail.outbox = []

    @patch('django.core.files.storage.default_storage.save')
    def test_upload_file(self, FileStorageMock):
        self.login_user()
        with open('gedgo/static/img/generic_person.gif') as fp:
            data = {
                'message': 'My test message',
                'uploads': fp
            }
            resp = self.client.post('/gedgo/%s/I1/' % self.gedcom.id, data)
            self.assertEqual(resp.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(
            message.subject,
            'Comment from Test User about John Doe (I1)'
        )
        self.assertTrue(
            message.body.endswith(
                'uploaded/test/%s/I1/generic_person.gif' % self.gedcom.id
            )
        )

        self.assertTrue(FileStorageMock.called)
        self.assertTrue(
            ('uploaded/test/%s/I1/generic_person.gif' % self.gedcom.id)
            in str(FileStorageMock.call_args))

    # TODO: Sort this test out
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True, BROKER_BACKEND='memory')
    def _test_dashboard_upload(self):
        self.login_user(set_super=True)
        with open('gedgo/static/test/test.ged') as fp:
            data = {
                'gedcom_id': self.gedcom.id,
                'gedcom_file': fp
            }
            with patch('settings.CELERY_ALWAYS_EAGER', True, create=True):
                resp = self.client.post('/gedgo/dashboard/', data)
        self.assertEqual(resp.status_code, 302, resp.content)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(
            message.subject,
            'Update finished!'
        )

        mail.outbox = []

        with open('gedgo/static/test/test.ged') as fp:
            data = {
                'gedcom_id': self.gedcom.id,
                'gedcom_file': fp,
                'email_users': '1',
                'message': 'Hi Mom!'
            }
            with patch('settings.CELERY_ALWAYS_EAGER', True, create=True):
                resp = self.client.post('/gedgo/dashboard/', data)
        self.assertEqual(resp.status_code, 302, resp.content)

        self.assertEqual(len(mail.outbox), 2)
        message = mail.outbox[0]
        self.assertEqual(
            message.subject,
            'Update finished!'
        )
        message = mail.outbox[1]
        self.assertEqual(
            [message.subject, message.body],
            ['Update to Test Gedcom',
             'Hi Mom!\n\nhttp://example.com/gedgo/1/']
        )
