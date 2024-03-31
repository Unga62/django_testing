import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.pytest_tests.conftest import COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, new_text_comment, news):
    url = reverse('news:detail', args=(news.pk,))
    client.post(url, data=new_text_comment)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client,
    new_text_comment,
    news,
    author
):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=new_text_comment)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == new_text_comment['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.pk,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, new_text_comment):
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, new_text_comment)
    comment.refresh_from_db()
    assert comment.text == new_text_comment['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    comment,
    new_text_comment
):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, new_text_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, slug_for_args):
    url = reverse('news:delete', args=slug_for_args)
    author_client.post(url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cant_delete_comment(not_author_client, slug_for_args):
    url = reverse('news:delete', args=slug_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
