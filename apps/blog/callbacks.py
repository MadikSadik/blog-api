import json
from typing import Any

from django.db.models import Count, Q
from django.http import HttpRequest
from django.urls import reverse

from apps.auths.models import User
from apps.blog.constants import (
    CHART_BAR_COLOR,
    ENV_COLOR_LOCAL,
    ENV_COLOR_PROD,
    ENV_ID_LOCAL,
    ENV_LABEL_LOCAL,
    ENV_LABEL_PROD,
    PERCENT,
    STATUS_DRAFT,
    STATUS_FILTER_PARAM,
    STATUS_PUBLISHED,
    TOP_AUTHORS_LIMIT,
)
from apps.blog.models import Category, Comment, Post
from settings import conf


def environment_callback(request: HttpRequest) -> list[str]:
    if conf.BLOG_ENV_ID == ENV_ID_LOCAL:
        return [ENV_LABEL_LOCAL, ENV_COLOR_LOCAL]
    return[ENV_LABEL_PROD, ENV_COLOR_PROD]

def drafts_badge(request: HttpRequest) -> int:
    return Post.objects.filter(status=Post.Status.DRAFT).count()

def superuser_only(request: HttpRequest) -> bool:
    return request.user.is_superuser

def published_tab_link(request: HttpRequest) -> str:
    return f'{reverse("admin:blog_post_changelist")}?{STATUS_FILTER_PARAM}={STATUS_PUBLISHED}'

def drafts_tab_link(request: HttpRequest) -> str:
    return f'{reverse("admin:blog_post_changelist")}?{STATUS_FILTER_PARAM}={STATUS_DRAFT}'


def dashboard_callback(request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
    counts = Post.objects.aggregate(
        published=Count('pk', filter=Q(status=Post.Status.PUBLISHED)),
        drafts=Count('pk', filter=Q(status=Post.Status.DRAFT)),
    )
    published = counts['published']
    drafts = counts['drafts']
    total = published + drafts
    published_percent = round(published * PERCENT / total) if total else 0

    categories = Category.objects.annotate(total=Count('post')).order_by('name')
    chart = {
        'labels': [category.name for category in categories],
        'datasets': [
            {
                'label': 'Posts',
                'data': [category.total for category in categories],
                'backgroundColor': CHART_BAR_COLOR,
            }
        ],
    }

    authors = User.objects.annotate(total=Count('post')).order_by('-total')[:TOP_AUTHORS_LIMIT]

    context.update(
        {
            'cards': [
                {'title': 'Users', 'value': User.objects.count()},
                {'title': 'Published posts', 'value': published},
                {'title': 'Drafts', 'value': drafts},
                {'title': 'Comments', 'value': Comment.objects.count()},
            ],
            'posts_chart': json.dumps(chart),
            'top_authors': {
                'headers': ['Author', 'Email', 'Posts'],
                'rows': [
                    [f'{user.first_name} {user.last_name}', user.email, user.total]
                    for user in authors
                ],
            },
            'progress': [
                {
                    'title': 'Published',
                    'description': f'{published_percent}%',
                    'value': published_percent,
                },
                {
                    'title': 'Drafts',
                    'description': f'{PERCENT - published_percent}%',
                    'value': PERCENT - published_percent,
                },
            ],
        }
    )
    return context
