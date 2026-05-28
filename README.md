# Django Notes App

A RESTful notes API built with Django REST Framework.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Endpoints

| Method | Endpoint          | Auth Required | Description          |
|--------|-------------------|---------------|----------------------|
| POST   | `/api/login`      | No            | Login, returns token |
| POST   | `/api/signup`     | No            | Register new user    |
| GET    | `/api/`           | Yes           | List user's notes    |
| POST   | `/api/`           | Yes           | Create a note        |
| GET    | `/api/note/<id>`  | Yes (owner)   | Retrieve a note      |
| PUT    | `/api/update/<id>`| Yes (owner)   | Update a note        |
| DELETE | `/api/delete/<id>`| Yes (owner)   | Delete a note        |

## Auth

Use `Authorization: Token <token>` header for authenticated requests.

## Environment Variables

| Variable         | Default                                                       | Description                       |
|------------------|---------------------------------------------------------------|-----------------------------------|
| `DJANGO_SECRET_KEY` | (development fallback)                                          | Django secret key                 |
| `DJANGO_DEBUG`   | `True`                                                        | Set to `False` in production      |
