from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

NOTES_COUNT: int = 5

User = get_user_model()


class TestContent(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Bob')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.author_two = User.objects.create(username='Jek')
        cls.auth_client_two = Client()
        cls.auth_client_two.force_login(cls.author_two)
        Note.objects.bulk_create(
            Note(
                title=f'Note{index}',
                text='TEXT',
                author=cls.author,
                slug=f'{index}'
            ) for index in range(NOTES_COUNT)
        )
        cls.note = Note.objects.create(
            title='Note1',
            text='TEXT',
            author=cls.author,
        )
        cls.note_two = Note.objects.create(
            title='Note2',
            text='TEXT',
            author=cls.author_two,
        )

    def test_note_in_notes(self):
        response = self.auth_client.get(self.LIST_URL)
        object_notes = response.context['object_list']
        self.assertIn(self.note, object_notes)

    def test_client_has_form(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_author_not_see_notes(self):
        response = self.auth_client.get(self.LIST_URL)
        object_notes = response.context['object_list']
        self.assertNotIn(self.note_two, object_notes)
