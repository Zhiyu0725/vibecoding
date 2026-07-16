# Blog System - Architecture

## High-Level Architecture

```
┌─────────────┐     HTTP      ┌─────────────┐     SQL      ┌─────────────┐
│   Browser   │ ────────────> │   Flask     │ ───────────> │   SQLite    │
│  (Client)   │ <──────────── │   App       │ <─────────── │  (blog.db)  │
└─────────────┘               └─────────────┘               └─────────────┘
```

## Directory Structure

```
blog/
├── app.py              # Flask application entry point
├── db.py               # Database connection & schema setup
├── auth.py             # Auth blueprint (register, login, logout)
├── posts.py            # Posts blueprint (create, list, view)
├── templates/
│   ├── base.html       # Base layout template
│   ├── register.html   # Registration form
│   ├── login.html      # Login form
│   ├── index.html      # Post listing (homepage)
│   ├── post.html       # Single post view
│   └── create.html     # Create post form
├── static/
│   └── style.css       # Stylesheet
├── blog.db             # SQLite database (auto-created)
└── docs/
    ├── proposal.md
    ├── architecture.md
    └── design.md
```

## Database Schema

### `users` Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| username | TEXT | UNIQUE NOT NULL |
| password_hash | TEXT | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### `posts` Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| title | TEXT | NOT NULL |
| body | TEXT | NOT NULL |
| author_id | INTEGER | FOREIGN KEY -> users(id) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Request Flow

### Registration
```
POST /register → validate input → hash password → INSERT user → redirect /login
```

### Login
```
POST /login → lookup user → verify password → set session → redirect /
```

### Create Post
```
POST /create → check session → validate input → INSERT post → redirect /
```

### View Posts
```
GET / → SELECT posts JOIN users → render index.html
```

## Authentication Model

- Server-side sessions via Flask `session` (signed cookies)
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Protected routes use a `login_required` decorator
- Session cookie stores `user_id`

## Security Considerations

- Passwords never stored in plaintext
- CSRF protection via Flask-WTF (optional, deferred to v2)
- SQL injection prevented by parameterized queries
- Session secret key loaded from environment variable
