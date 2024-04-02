from django.conf import settings
import pytest

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, news_list, news_home_url):
    response = client.get(news_home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list, news_home_url):
    response = client.get(news_home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, news_detail_url):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_client_has_form(
    parametrized_client,
    status,
    comment,
    admin_client,
    comment_url
):
    response = parametrized_client.get(comment_url)
    assert isinstance(
        admin_client.get(comment_url).context['form'], CommentForm
    )
    assert ('form' in response.context) is status
