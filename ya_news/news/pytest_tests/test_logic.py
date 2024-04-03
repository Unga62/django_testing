from random import choice

from pytest_django.asserts import assertRedirects, assertFormError
import pytest

from news.models import Comment
from news.pytest_tests.conftest import (
    COMMENT_COUNT,
    NEW_TEXT_COMMENT,
    NOT_FOUND
)

from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, news_detail_url):
    initial_count = Comment.objects.count()
    client.post(news_detail_url, data=NEW_TEXT_COMMENT)
    comments_count = Comment.objects.count()
    assert initial_count == comments_count


def test_user_can_create_comment(
    author_client,
    news,
    author,
    news_detail_url
):
    initial_count = Comment.objects.count() + COMMENT_COUNT
    response = author_client.post(news_detail_url, data=NEW_TEXT_COMMENT)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert initial_count == comments_count
    comment = Comment.objects.last()
    assert comment.text == NEW_TEXT_COMMENT['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, news_detail_url):
    initial_count = Comment.objects.count()
    bad_words_data = {'text': f'{choice(BAD_WORDS)}'}
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert initial_count == comments_count


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_comment_url,
    news,
    author
):
    author_client.post(edit_comment_url, NEW_TEXT_COMMENT)
    comment.refresh_from_db()
    assert comment.text == NEW_TEXT_COMMENT['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    comment,
    edit_comment_url
):
    response = not_author_client.post(edit_comment_url, NEW_TEXT_COMMENT)
    assert response.status_code == NOT_FOUND
    comment_edit = Comment.objects.get(id=comment.pk)
    assert comment_edit.text == comment.text
    assert comment_edit.author == comment.author
    assert comment_edit.news == comment.news


def test_author_can_delete_comment(author_client, comment, delete_comment_url):
    initial_count = Comment.objects.count() - COMMENT_COUNT
    author_client.post(delete_comment_url)
    comments_count = Comment.objects.count()
    assert initial_count == comments_count


def test_other_user_cant_delete_comment(
    not_author_client,
    comment,
    delete_comment_url
):
    initial_count = Comment.objects.count()
    response = not_author_client.post(delete_comment_url)
    assert response.status_code == NOT_FOUND
    comments_count = Comment.objects.count()
    assert initial_count == comments_count
