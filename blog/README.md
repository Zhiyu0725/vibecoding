# Blog

A lightweight blog system with user authentication, built with Flask and SQLite.

## Prerequisites

- Python 3.9+

## Install

```bash
cd blog
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open [http://localhost:5001](http://localhost:5001) in your browser.

## Features

- Register and log in
- Create posts (logged-in users only)
- View all posts on the homepage
- Read individual posts

## Project Structure

```
blog/
├── app.py           # Flask entry point
├── db.py            # SQLite schema & connection
├── auth.py          # Authentication (register, login, logout)
├── posts.py         # Post CRUD operations
├── requirements.txt # Python dependencies
├── blog.db          # SQLite database (auto-created)
├── static/style.css # Stylesheet
└── templates/       # Jinja2 HTML templates
```

## Reset Database

```bash
rm blog.db
python app.py
```

The database is recreated automatically on startup.
