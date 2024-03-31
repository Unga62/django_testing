from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note

User = get_user_model()

URLS_ADD_LIST_SUCCESS = (
    ('notes:add', None),
    ('notes:list', None),
    ('notes:success', None),
)

URLS_EDIT_DELETE_DETAIL = (
    'notes:edit',
    'notes:delete',
    'notes:detail'
)


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Джек')
        cls.visitor = User.objects.create(username='Посетитель')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Новая заметка',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_edit_create(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.visitor, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in URLS_EDIT_DELETE_DETAIL:
                with self.subTest(name=name, user=user):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_add_list_done(self):
        self.client.force_login(self.author)
        for name, args in URLS_ADD_LIST_SUCCESS:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for urls in (URLS_EDIT_DELETE_DETAIL, URLS_ADD_LIST_SUCCESS):
            if urls in URLS_ADD_LIST_SUCCESS:
                for name, args in URLS_ADD_LIST_SUCCESS:
                    url = reverse(name, args=args)
            else:
                for name in URLS_EDIT_DELETE_DETAIL:
                    url = reverse(name, args=(self.note.slug,))
            with self.subTest(name=name):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
