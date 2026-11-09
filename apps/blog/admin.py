from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
from unfold.sections import TableSection

from django.contrib import admin
from django.db import models
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.text import Truncator

from apps.blog.constants import (
    COMMENT_BODY_PREVIEW_LENGTH,
    POST_FILTER_PARAM,
    STATUS_DRAFT,
    STATUS_PUBLISHED,
)
from apps.blog.models import Category, Comment, Post, Tag


class CategoryPostsSection(TableSection):
    verbose_name = 'Posts'
    related_name = 'post_set'
    fields = ['title', 'status', 'created_at']


class PostsCountAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'posts_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(posts_total=Count('post'))

    @display(description='Posts', ordering='posts_total')
    def posts_count(self, obj: Category | Tag) -> int:
        return obj.posts_total


@admin.register(Category)
class CategoryAdmin(PostsCountAdmin):
    list_sections = [CategoryPostsSection]


@admin.register(Tag)
class TagAdmin(PostsCountAdmin):
    pass


class PostCommentsSection(TableSection):
    verbose_name = 'Comments'
    related_name = 'comment_set'
    fields = ['body', 'created_at']



class CommentInline(TabularInline):
    model = Comment
    tab = True
    per_page = 10
    extra = 0
    fields = ('author', 'body', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('author',)

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        'post_header',
        'status_label',
        'category',
        'tags_dropdown',
        'comments_count',
        'created_at',
    )
    list_select_related = ('author', 'category')
    list_filter = [
        ('status', ChoicesDropdownFilter),
        ('category', RelatedDropdownFilter),
        ('tags', MultipleRelatedDropdownFilter),
        ('author', AutocompleteSelectFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    list_filter_submit = True
    list_sections = [PostCommentsSection]
    search_fields = ('title', 'body', 'author__email')

    actions = ['publish_selected', 'move_to_drafts']
    actions_list = ['publish_all_drafts']
    actions_row = ['toggle_publish']
    actions_detail = ['open_comments']
    actions_submit_line = ['save_and_publish']

    inlines = [CommentInline]
    autocomplete_fields = ('author', 'category', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    warn_unsaved_form = True
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }
    fieldsets = (
        ('Content', {'classes': ['tab'], 'fields': ('title', 'slug', 'body')}),
        ('Classification', {'classes': ['tab'], 'fields': ('category', 'tags', 'status')}),
        ('Meta', {'classes': ['tab'], 'fields': ('author', 'created_at', 'updated_at')}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .annotate(comments_total=Count('comment'))
            .prefetch_related('tags', 'comment_set')
        )

    @display(description='Post', header=True, ordering='title')
    def post_header(self, obj: Post) -> list[str]:
        author = obj.author
        initials = (author.first_name[:1] + author.last_name[:1]).upper()
        return [obj.title, author.email, initials]

    @display(
        description='Status',
        ordering='status',
        label={STATUS_PUBLISHED: 'success', STATUS_DRAFT: 'warning'},
    )
    def status_label(self, obj: Post) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description='Tags', dropdown=True)
    def tags_dropdown(self, obj: Post) -> dict:
        tags = obj.tags.all()
        return {
            'title': f'{len(tags)} tags',
            'items': [{'title': tag.name} for tag in tags],
        }

    @display(description='Comments', ordering='comments_total')
    def comments_count(self, obj: Post) -> int:
        return obj.comments_total

    @action(description='Publish selected')
    def publish_selected(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(status=Post.Status.PUBLISHED)
        self.message_user(request, f'{updated} posts published.')

    @action(description='Move to drafts')
    def move_to_drafts(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated = queryset.update(status=Post.Status.DRAFT)
        self.message_user(request, f'{updated} posts moved to drafts.')

    @action(description='Publish all drafts')
    def publish_all_drafts(self, request: HttpRequest) -> HttpResponse:
        updated = Post.objects.filter(status=Post.Status.DRAFT).update(
            status=Post.Status.PUBLISHED
        )
        self.message_user(request, f'{updated} drafts published.')
        return redirect(reverse('admin:blog_post_changelist'))

    @action(description='Publish / unpublish', url_path='toggle-publish')
    def toggle_publish(self, request: HttpRequest, object_id: int) -> HttpResponse:
        post = get_object_or_404(Post, pk=object_id)
        if post.status == Post.Status.PUBLISHED:
            post.status = Post.Status.DRAFT
        else:
            post.status = Post.Status.PUBLISHED
        post.save(update_fields=['status', 'updated_at'])
        return redirect(reverse('admin:blog_post_changelist'))

    @action(description='Open comments', url_path='open-comments')
    def open_comments(self, request: HttpRequest, object_id: int) -> HttpResponse:
        url = reverse('admin:blog_comment_changelist')
        return redirect(f'{url}?{POST_FILTER_PARAM}={object_id}')

    @action(description='Save & publish')
    def save_and_publish(self, request: HttpRequest, obj: Post) -> None:
        obj.status = Post.Status.PUBLISHED
        obj.save(update_fields=['status', 'updated_at'])


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('post_title', 'author', 'short_body', 'created_at')
    list_select_related = ('post', 'author')
    list_filter = [
        ('post', AutocompleteSelectFilter),
        ('author', AutocompleteSelectFilter),
        ('created_at', RangeDateTimeFilter),
    ]
    list_filter_submit = True
    search_fields = ('body', 'author__email', 'post__title')
    autocomplete_fields = ('post', 'author')

    @display(description='Post', ordering='post__title')
    def post_title(self, obj: Comment) -> str:
        return obj.post.title

    @display(description='Body')
    def short_body(self, obj: Comment) -> str:
        return Truncator(obj.body).chars(COMMENT_BODY_PREVIEW_LENGTH)
