import random
import time
from typing import Any

from faker import Faker

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.text import slugify

from apps.auths.models import User
from apps.blog.constants import (
    CATEGORY_NAMES,
    DEFAULT_COMMENTS,
    DEFAULT_POSTS,
    DEFAULT_USERS,
    INACTIVE_USER_RATIO,
    MAX_COMMENT_SENTENCES,
    MAX_PARAGRAPHS,
    MAX_TAGS_PER_POST,
    MIN_COMMENT_SENTENCES,
    MIN_PARAGRAPHS,
    NEGATIVE_NUMBER_ERROR,
    NO_CATEGORY_RATIO,
    NO_PUBLISHED_POSTS_ERROR,
    NO_USERS_ERROR,
    PUBLISHED_POST_RATIO,
    SEED_EMAIL_DOMAIN,
    SEED_PASSWORD,
    SLUG_BASE_MAX_LENGTH,
    STAFF_USER_RATIO,
    SUMMARY_LABEL_WIDTH,
    SUMMARY_NUMBER_WIDTH,
    TAG_NAMES,
    TITLE_WORDS,
)
from apps.blog.models import Category, Comment, Post, Tag


class Command(BaseCommand):
    help = 'Fill the database with fake data.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--users', type=int, default=DEFAULT_USERS, help='Number of users to create'
        )
        parser.add_argument(
            '--posts', type=int, default=DEFAULT_POSTS, help='Number of posts to create'
        )
        parser.add_argument(
            '--comments', type=int, default=DEFAULT_COMMENTS, help='Number of comments to create'
        )
        parser.add_argument(
            '--clear', action='store_true', help='Delete existing data before seeding'
        )

    def handle(self, *args: Any, **options: Any) -> None:
        users_count: int = options['users']
        posts_count: int = options['posts']
        comments_count: int = options['comments']
        clear: bool = options['clear']

        start_time = time.perf_counter()

        counts = {'users': users_count, 'posts': posts_count, 'comments': comments_count}
        for name, value in counts.items():
            if value < 0:
                raise CommandError(NEGATIVE_NUMBER_ERROR.format(name=name))

        if clear:
            self.clear_data()

        created_users = self.create_users(users_count)

        if (posts_count or comments_count) and not User.objects.exists():
            raise CommandError(NO_USERS_ERROR)

        created_categories = self.create_named_items(Category, CATEGORY_NAMES)
        created_tags = self.create_named_items(Tag, TAG_NAMES)
        created_posts = self.create_posts(posts_count)

        if comments_count and not Post.objects.filter(status=Post.Status.PUBLISHED).exists():
            raise CommandError(NO_PUBLISHED_POSTS_ERROR)
        created_comments = self.create_comments(comments_count)

        summary = {
            'Users': created_users,
            'Categories': created_categories,
            'Tags': created_tags,
            'Posts': created_posts,
            'Comments': created_comments,
        }
        for label, number in summary.items():
            name = f'{label}:'.ljust(SUMMARY_LABEL_WIDTH)
            value = f'{number:>{SUMMARY_NUMBER_WIDTH}}'
            self.stdout.write(self.style.SUCCESS(f'{name}{value} created'))

        elapsed = time.perf_counter() - start_time
        self.stdout.write(self.style.SUCCESS(f'Done in {elapsed:.2f} seconds'))

    def clear_data(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, count: int) -> int:
        fake = Faker()
        password = make_password(SEED_PASSWORD)
        used_emails = set(User.objects.values_list('email', flat=True))
        users: list[User] = []

        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            base = f'{first_name}.{last_name}'.lower().replace(' ', '')
            email = f'{base}@{SEED_EMAIL_DOMAIN}'
            number = 2
            while email in used_emails:
                email = f'{base}{number}@{SEED_EMAIL_DOMAIN}'
                number += 1
            used_emails.add(email)

            users.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    is_active=random.random() >= INACTIVE_USER_RATIO,
                    is_staff=random.random() < STAFF_USER_RATIO,
                )
            )
        User.objects.bulk_create(users)
        return len(users)


    def create_named_items(self, model: type[Category] | type[Tag], names: tuple[str, ...]) -> int:
        existing_names = set(model.objects.values_list('name', flat=True))
        items = [
            model(name=name, slug=slugify(name))
            for name in names
            if name not in existing_names
        ]
        model.objects.bulk_create(items)
        return len(items)


    def create_posts(self, count: int) -> int:
        fake = Faker()
        users = list(User.objects.all())
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        used_slugs = set(Post.objects.values_list('slug', flat=True))
        posts: list[Post] = []
        posts_tags: list[list[Tag]] = []

        for _ in range(count):
            title = fake.sentence(nb_words=TITLE_WORDS).rstrip('.')
            base_slug = slugify(title)[:SLUG_BASE_MAX_LENGTH]
            slug = base_slug
            number = 2
            while slug in used_slugs:
                slug = f'{base_slug}-{number}'
                number += 1
            used_slugs.add(slug)

            paragraphs = fake.paragraphs(nb=random.randint(MIN_PARAGRAPHS, MAX_PARAGRAPHS))
            is_published = random.random() < PUBLISHED_POST_RATIO
            has_category = random.random() >= NO_CATEGORY_RATIO

            posts.append(
                Post(
                    author=random.choice(users),
                    title=title,
                    slug=slug,
                    body='\n\n'.join(paragraphs),
                    category=random.choice(categories) if has_category else None,
                    status=Post.Status.PUBLISHED if is_published else Post.Status.DRAFT,
                )
            )
            posts_tags.append(random.sample(tags, k=random.randint(0, MAX_TAGS_PER_POST)))

        Post.objects.bulk_create(posts)
        for post, post_tags in zip(posts, posts_tags):
            post.tags.set(post_tags)
        return len(posts)

    def create_comments(self, count: int) -> int:
        fake = Faker()
        users = list(User.objects.all())
        published_posts = list(Post.objects.filter(status=Post.Status.PUBLISHED))
        comments: list[Comment] = []

        for _ in range(count):
            sentences = random.randint(MIN_COMMENT_SENTENCES, MAX_COMMENT_SENTENCES)
            comments.append(
                Comment(
                    post=random.choice(published_posts),
                    author=random.choice(users),
                    body=' '.join(fake.sentences(nb=sentences)),
                )
            )

        Comment.objects.bulk_create(comments)
        return len(comments)
