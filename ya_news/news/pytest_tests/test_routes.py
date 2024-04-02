from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.test.client import Client
import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (pytest.lazy_fixture('news_home_url'), Client(), HTTPStatus.OK),
        (pytest.lazy_fixture('user_login'), Client(), HTTPStatus.OK),
        (pytest.lazy_fixture('users_logout'), Client(), HTTPStatus.OK),
        (pytest.lazy_fixture('users_signup'), Client(), HTTPStatus.OK),
        (pytest.lazy_fixture('news_detail_url'), Client(), HTTPStatus.OK),
        (
            pytest.lazy_fixture('delete_comment_url'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('edit_comment_url'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('delete_comment_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('edit_comment_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
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
    'name, comment_object',
    (
        ('news:delete', pytest.lazy_fixture('comment')),
        ('news:edit', pytest.lazy_fixture('comment')),
    ),
)
def test_redirects(client, name, comment_object):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_object.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
