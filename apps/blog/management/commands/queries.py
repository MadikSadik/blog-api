from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import connection
from django.db.models import Count, QuerySet
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from django.utils.text import slugify

from apps.blog.constants import (
    CATEGORY_NAMES,
    CHANGING_QUERY_NUMBERS,
    NO_DATA_ERROR,
    PREVIEW_ROWS,
    SAMPLE_DAYS,
    SAMPLE_MIN_POSTS,
    SAMPLE_TAG_NAME,
    SEED_EMAIL_DOMAIN,
    UNKNOWN_QUERY_ERROR,
)
from apps.blog.models import Post
from apps.blog.queries import QUERIES


class Command(BaseCommand):
    help = 'Run the homework queries.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--number', type=int, help='Run only this query')
        parser.add_argument('--sql', action='store_true', help='Print the SQL')

    def handle(self, *args: Any, **options: Any) -> None:
        number = options['number']
        if number is None:
            numbers = [n for n in QUERIES if n not in CHANGING_QUERY_NUMBERS]
        elif number in QUERIES:
            numbers = [number]
        else:
            raise CommandError(UNKNOWN_QUERY_ERROR.format(number=number))

        arguments = self.get_arguments()
        for n in numbers:
            self.run_query(n, arguments.get(n, {}), options['sql'])

    def get_arguments(self) -> dict[int, dict[str, Any]]:
        post = Post.objects.filter(status=Post.Status.PUBLISHED).first()
        if post is None:
            raise CommandError(NO_DATA_ERROR)
        tagged_post = Post.objects.annotate(tag_count=Count('tags')).order_by('-tag_count').first()
        tag_slugs = list(tagged_post.tags.values_list('slug', flat=True))
        today = timezone.now().date()
        author = post.author
        return {
            4: {'slug': post.slug},
            7: {'page': 2},
            8: {'word': post.title.split()[0]},
            9: {'domain': SEED_EMAIL_DOMAIN},
            11: {'slugs': [slugify(name) for name in CATEGORY_NAMES[:2]]},
            12: {'year': post.created_at.year, 'month': post.created_at.month},
            13: {'days': SAMPLE_DAYS},
            14: {'start': today - timedelta(days=SAMPLE_DAYS), 'end': today},
            15: {'email': post.author.email},
            16: {'tag_slug': tag_slugs[0]},
            17: {'category_slug': slugify(CATEGORY_NAMES[0])},
            21: {'first_slug': tag_slugs[0], 'second_slug': tag_slugs[1]},
            22: {'text': post.title.split()[0]},
            34: {'min_posts': SAMPLE_MIN_POSTS},
            37: {'text': f'{author.first_name} {author.last_name}'.lower()},
            40: {'name': SAMPLE_TAG_NAME},
            41: {'days': SAMPLE_DAYS},
            42: {'category_slug': slugify(CATEGORY_NAMES[0]), 'tag_slug': tag_slugs[0]},
            43: {
                'source_slug': slugify(CATEGORY_NAMES[-1]),
                'target_slug': slugify(CATEGORY_NAMES[0]),
            },
        }

    def run_query(self, number: int, arguments: dict[str, Any], show_sql: bool) -> None:
        function = QUERIES[number]
        annotations: list[str] = []
        with CaptureQueriesContext(connection) as context:
            result = function(**arguments)
            if isinstance(result, QuerySet):
                annotations = list(result.query.annotations)
                result = list(result)

        count = len(context.captured_queries)
        word = 'query' if count == 1 else 'queries'
        self.stdout.write(self.style.SUCCESS(f'#{number} {function.__name__} — {count} SQL {word}'))
        if show_sql:
            for query in context.captured_queries:
                self.stdout.write(query['sql'])
        self.show_result(result, annotations)

    def show_result(self, result: Any, annotations: list[str]) -> None:
        if not isinstance(result, list):
            self.stdout.write(f'  {result}')
            return
        for row in result[:PREVIEW_ROWS]:
            values = {name: getattr(row, name) for name in annotations}
            self.stdout.write(f'  {row} {values}' if values else f'  {row}')
        self.stdout.write(f'  ({len(result)} rows)')
