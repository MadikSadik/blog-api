# blog-api
Django projects

![ERD](docs/erd.png)

## Quick start

```bash
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/admin/ and log in.

## Seeding

The `seed` command fills the database with fake data (users, categories, tags, posts and comments).

```bash
python manage.py seed
python manage.py seed --users 50 --posts 300 --comments 1500
python manage.py seed --clear
```

| Argument | Description |
|---|---|
| `--users N` | Number of users to create |
| `--posts N` | Number of posts to create |
| `--comments N` | Number of comments to create |
| `--clear` | Delete existing data before seeding (superusers are kept) |

Notes:
- All arguments are optional and have default values.
- Negative numbers are rejected with an error.
- Seeded users have emails like `name.surname@example.com` and the password `seedpass123`.
- Posts get random dates in the last 365 days, and comments are created after their post.
- At the end the command prints a summary of what was created and how long it took.

## Admin
The admin panel uses [Django Unfold](https://github.com/unfoldadmin/django-unfold).
It has a sidebar, a status tab filter for posts and a "LOCAL" / "PROD" environment label.

### Dashboard
Cards with totals, a chart of posts per category, the top 5 authors and the published/drafts ratio.

![Dashboard](docs/screenshots/dashboard.png)

### Posts
Tabs (All / Published / Drafts), filters by status, category, tags, author and date,
search, bulk actions (publish, move to drafts) and a rich text editor for the body.
Comments are shown on the post page.

![Post list](docs/screenshots/post-list.png)

![Post edit](docs/screenshots/post-edit.png)

### Users
Active and staff status labels, number of posts per user, filters, search
and actions to activate or deactivate users.

![User list](docs/screenshots/user-list.png)

## Queries
The `queries` command runs the 50 ORM queries from `apps/blog/queries.py`
and shows the result and the number of SQL queries.

```bash
python manage.py queries                    # all queries except 40-44 (they change the data)
python manage.py queries --number 31        # only query 31 (works for 40-44 too)
python manage.py queries --number 6 --sql   # also print the SQL
```

Example:

```
$ python manage.py queries --number 31
#31 categories_with_post_count — 1 SQL query
  Machine Learning {'post_count': 17}
  Django {'post_count': 14}
  Security {'post_count': 12}
  DevOps {'post_count': 10}
  Python {'post_count': 9}
  (8 rows)
```

Queries 40–44 change the data. To get fresh data, run `python manage.py seed --clear`.