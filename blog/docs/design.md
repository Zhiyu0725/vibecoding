# Blog System - Design Document

## UI/UX Design

### Pages

#### 1. Homepage (`/`)
- List of all posts, newest first
- Each card shows: title, author, date, body preview (first 200 chars)
- Navbar: Home | Create Post (if logged in) | Login/Register or Logout

#### 2. Register (`/register`)
- Form fields: username, password, confirm password
- Validation: username 3-20 chars, password 6+ chars, passwords match
- Link to login if already have account

#### 3. Login (`/login`)
- Form fields: username, password
- Link to register if no account
- Error message on invalid credentials

#### 4. Create Post (`/create`)
- Redirect to `/login` if not authenticated
- Form fields: title, body (textarea)
- Validation: title 1-200 chars, body non-empty

#### 5. Single Post (`/post/<id>`)
- Full post content
- Author name and date
- Back to homepage link

### Color Palette

```
Background:   #f5f5f5
Card/Content: #ffffff
Primary:      #2563eb (blue)
Text:         #1f2937 (dark gray)
Muted:        #6b7280 (gray)
Border:       #e5e7eb
```

### Typography

```
Headings: 'Georgia', serif
Body:     'system-ui', sans-serif
Code:     'Menlo', monospace
```

## API Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Homepage - list posts |
| GET | `/register` | No | Registration form |
| POST | `/register` | No | Process registration |
| GET | `/login` | No | Login form |
| POST | `/login` | No | Process login |
| GET | `/logout` | Yes | Destroy session |
| GET | `/create` | Yes | Create post form |
| POST | `/create` | Yes | Process new post |
| GET | `/post/<id>` | No | View single post |

## Data Validation

### Registration
- `username`: alphanumeric + underscores, 3-20 chars, unique
- `password`: min 6 chars, hashed before storage

### Post
- `title`: 1-200 chars, stripped of leading/trailing whitespace
- `body`: non-empty, stored as-is (plain text)

## Error Handling

- 400: Bad request / validation errors → flash message + redirect
- 401: Unauthorized access → redirect to `/login`
- 404: Post not found → simple "Not Found" page
- 500: Server error → generic error page

## Future Enhancements (v2)

- Post edit/delete (owner only)
- Comments system
- Markdown support for post body
- Pagination (10 posts per page)
- User profile pages
- Search functionality
