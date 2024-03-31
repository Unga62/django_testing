from pytils.translit import slugify

from http import HTTPStatus

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogicCreate(TestCase):

    NOTE_TEXT = 'TEXT'
    NOTE_SLUG = 'NOTE'
    NOTE_TITLE = 'TITLE'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_author_create_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.slug, self.NOTE_SLUG)


class TestLogicEditDeleteUnique(TestCase):

    OLD_TEXT = 'Old text'
    NEW_TEXT = 'New text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.author_two = User.objects.create(username='Второй автор')
        cls.auth_client_two = Client()
        cls.auth_client_two.force_login(cls.author_two)
        cls.note = Note.objects.create(
            title='notes',
            text=cls.OLD_TEXT,
            author=cls.author,
        )
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_success = reverse('notes:success')
        cls.form_data = {
            'title': 'title',
            'text': cls.NEW_TEXT,
            'slug': 'slug'
        }

    def test_slug_unique(self):
        response = self.auth_client.post(
            self.url_add,
            data={
                'title': 'new_note',
                'text': 'new_text',
                'slug': self.note.slug
            }
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_delete_author_note(self):
        response = self.auth_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 0)

    def test_delete_authortwo_note(self):
        response = self.auth_client_two.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_edit_author(self):
        response = self.auth_client.post(
            self.url_edit,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_edit_author_two(self):
        response = self.auth_client_two.post(
            self.url_edit,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.OLD_TEXT)


class TestEmptySlug(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.form_data = {
            'title': 'title',
            'text': 'text',
        }

    def test_empty_slug(self):
        response = self.auth_client.post(
            self.url_add,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
