from http import HTTPStatus

from pytest_django.asserts import assertRedirects
import pytest
from pytest_lazyfixture import lazy_fixture as lf
from django.test.client import Client

from news.pytest_tests.conftest import (
    SUCCESS,
    NOT_FOUND,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (lf('news_home_url'), Client(), SUCCESS),
        (lf('user_login'), Client(), SUCCESS),
        (lf('users_logout'), Client(), SUCCESS),
        (lf('users_signup'), Client(), SUCCESS),
        (lf('news_detail_url'), Client(), SUCCESS),
        (
            lf('delete_comment_url'),
            lf('not_author_client'),
            NOT_FOUND
        ),
        (
            lf('edit_comment_url'),
            lf('not_author_client'),
            NOT_FOUND
        ),
        (
            lf('delete_comment_url'),
            lf('author_client'),
            SUCCESS
        ),
        (
            lf('edit_comment_url'),
            lf('author_client'),
            SUCCESS
        ),
    )
)
def test_pages_availability_for_anonymous_user(
    reverse_url,
    parametrized_client,
    status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'reverse_url, comment_object',
    (
        (lf('delete_comment_url'), lf('comment')),
        (lf('edit_comment_url'), lf('comment')),
    ),
)
def test_redirects(client, reverse_url, comment_object, user_login):
    expected_url = f'{user_login}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, expected_url)
