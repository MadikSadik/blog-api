CATEGORY_NAME_MAX_LENGTH = 100
TAG_NAME_LENGTH = 50
POST_TITLE_MAX_LENGTH = 200
POST_STATUS_MAX_LENGTH = 20

STATUS_DRAFT = 'draft'
STATUS_PUBLISHED = 'published'

DEFAULT_USERS = 20
DEFAULT_POSTS = 100
DEFAULT_COMMENTS = 500

NEGATIVE_NUMBER_ERROR = 'Argument --{name} must not be negative.'

SEED_PASSWORD = 'seedpass123'
SEED_EMAIL_DOMAIN = 'example.com'
INACTIVE_USER_RATIO = 0.1
STAFF_USER_RATIO = 0.1


CATEGORY_NAMES = (
    'Python',
    'Django',
    'DevOps',
    'Databases',
    'Frontend',
    'Machine Learning',
    'Testing',
    'Security',
)

TAG_NAMES = (
    'Tutorial',
    'Beginner',
    'Tips',
    'Performance',
    'Debugging',
    'Deployment',
    'Cloud',
    'Automation',
    'Open Source',
    'Algorithms',
    'Architecture',
    'Career',
    'Productivity',
    'Tools',
    'Refactoring',
    'Async',
    'Caching',
    'Scalability',
    'REST API',
)


PUBLISHED_POST_RATIO = 0.7
NO_CATEGORY_RATIO = 0.1
MAX_TAGS_PER_POST = 5
MIN_PARAGRAPHS = 3
MAX_PARAGRAPHS = 6
TITLE_WORDS = 6
SLUG_BASE_MAX_LENGTH = 40

NO_USERS_ERROR = 'Posts and comments need at least one user. Use --users.'


MIN_COMMENT_SENTENCES = 1
MAX_COMMENT_SENTENCES = 3
SUMMARY_LABEL_WIDTH = 12
SUMMARY_NUMBER_WIDTH = 5

NO_PUBLISHED_POSTS_ERROR = 'Comments need at least one published post. Use --posts.'
