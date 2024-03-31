from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note
from notes.forms import NoteForm

NOTES_COUNT: int = 5

User = get_user_model()


class TestContent(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Bob')
        cls.author_two = User.objects.create(username='Jek')
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

    def test_note_in_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_client_has_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_author_not_see_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertFalse(self.author_two is (self.note in object_list))
