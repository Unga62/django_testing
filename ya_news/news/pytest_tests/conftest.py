import pytest

from django.test.client import Client

from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from news.models import Comment, News

NEW_TEXT_COMMENT = 'Просто текст'
COMMENT_TEXT = 'Текст комментария'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def comment(author, news):
    new_commnet = Comment.objects.create(
        text=COMMENT_TEXT,
        author=author,
        news=news
    )
    return new_commnet


@pytest.fixture
def slug_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def news_list():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    for index in range(5):
        comment = Comment.objects.create(
            text=f'Comment {index}',
            news=news,
            author=author
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def new_text_comment():
    return {'text': NEW_TEXT_COMMENT}
