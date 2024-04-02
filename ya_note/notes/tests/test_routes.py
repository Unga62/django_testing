from http import HTTPStatus

from django.contrib.auth import get_user_model, get_user
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.visitor = User.objects.create(username='Посетитель')
        cls.auth_visitor = Client()
        cls.auth_visitor.force_login(cls.visitor)
        cls.note = Note.objects.create(
            title='Заметка',
            text='Новая заметка',
            author=cls.author
        )
        cls.URLS_REDIRECT = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
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
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_edit_create(self):
        users_statuses = (
            (self.auth_client, HTTPStatus.OK),
            (self.auth_visitor, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in URLS_EDIT_DELETE_DETAIL:
                with self.subTest(
                    name=name,
                    user=get_user(user),
                    status=status
                ):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_add_list_done(self):
        for name, args in URLS_ADD_LIST_SUCCESS:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_visitor.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in self.URLS_REDIRECT:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
