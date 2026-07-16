# Blog System - Project Proposal

## Overview

A lightweight blog system built with Python and SQLite, featuring user authentication and post management.

## Goals

- Provide a simple, self-contained blog platform
- SQLite for zero-config, portable storage
- Secure user registration and login (password hashing)
- Only authenticated users can create posts
- Clean, minimal web interface

## Core Features

| Feature | Description |
|---------|-------------|
| Register | Users create an account (username + password) |
| Login/Logout | Session-based authentication |
| Create Post | Logged-in users write blog posts (title + body) |
| View Posts | Public feed of all posts with author info |
| View Post | Single post page with full content |

## Tech Stack

- **Backend**: Python 3 + Flask
- **Database**: SQLite3 (via Python's built-in `sqlite3` module)
- **Auth**: Flask sessions + `werkzeug.security` for password hashing
- **Templates**: Jinja2 (Flask default)
- **Frontend**: Plain HTML + CSS (no JS frameworks)

## Out of Scope (v1)

- Post editing / deletion
- Comments
- User profiles / avatars
- Rich text editor
- Pagination

## Success Criteria

1. User can register and log in
2. Logged-in user can create a post
3. All visitors can read posts
4. Data persists in SQLite file
