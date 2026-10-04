from pathlib import Path

from decouple import Config, RepositoryEnv, Csv

ENV_FILE = Path(__file__).resolve().parent / '.env'
config = Config(RepositoryEnv(ENV_FILE))

BLOG_ENV_ID: str = config('BLOG_ENV_ID', default='local')
BLOG_SECRET_KEY: str = config('BLOG_SECRET_KEY')
BLOG_ALLOWED_HOSTS: list[str] = config('BLOG_ALLOWED_HOSTS', cast=Csv(), default='')

BLOG_DB_NAME: str = config('BLOG_DB_NAME', default='')
BLOG_DB_USER: str = config('BLOG_DB_USER', default='')
BLOG_DB_PASSWORD: str = config('BLOG_DB_PASSWORD', default='')
BLOG_DB_HOST: str = config('BLOG_DB_HOST', default='')
BLOG_DB_PORT: str = config('BLOG_DB_PORT', default='')