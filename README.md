# Coderr API

Backend for Coderr, a marketplace where business users publish service offers and
customers order them and leave reviews. The project is a Django REST Framework
API; the frontend is a separate application that talks to it over HTTP.

- **Framework:** Django 6.1 with Django REST Framework 3.18
- **Authentication:** DRF token authentication
- **Database:** SQLite (no external service required)
- **Python:** 3.12 or newer

---

## Table of contents

- [Setup](#setup)
  - [1. Get the code](#1-get-the-code)
  - [2. Create a virtual environment](#2-create-a-virtual-environment)
  - [3. Install the dependencies](#3-install-the-dependencies)
  - [4. Create the `.env` file](#4-create-the-env-file)
  - [5. Create the database](#5-create-the-database)
  - [6. Create an admin account](#6-create-an-admin-account)
  - [7. Start the server](#7-start-the-server)
- [Running the tests](#running-the-tests)
- [Environment variables](#environment-variables)
- [Project layout](#project-layout)
- [Authentication](#authentication)
- [User roles](#user-roles)
- [API reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## Setup

Every command is run from the project root, the folder that contains
`manage.py`.

### 1. Get the code

```bash
git clone <repository-url>
cd coderr
```

### 2. Create a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv env
env\Scripts\Activate.ps1
```

If PowerShell refuses to run the activation script, allow it for the current
user once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (Command Prompt)**

```bat
python -m venv env
env\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv env
source env/bin/activate
```

The prompt now starts with `(env)`. Everything below assumes the environment is
active; `deactivate` leaves it again.

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

On Windows use `python -m pip install -r requirements.txt` if `pip` is not on the
PATH.

### 4. Create the `.env` file

Copy the template and fill in a secret key:

**Windows (PowerShell)**

```powershell
Copy-Item .env.template .env
```

**macOS / Linux**

```bash
cp .env.template .env
```

Generate a key and paste it into `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

A working development `.env` looks like this:

```ini
SECRET_KEY=your-generated-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

`CORS_ALLOWED_ORIGINS` has to contain the exact origin the frontend is served
from, including protocol and port. A wrong entry here is the usual cause of the
frontend loading but every request failing.

The server will not start without a `SECRET_KEY`.

### 5. Create the database

Migrations are not tracked in version control, so they are generated on first
setup:

```bash
python manage.py makemigrations accounts offers orders reviews
python manage.py migrate
```

This creates `db.sqlite3` in the project root.

### 6. Create an admin account

```bash
python manage.py createsuperuser
```

The command asks for a username, an email address and a `type`, which has to be
either `business` or `customer`. The account is reachable at
`http://127.0.0.1:8000/admin/`.

### 7. Start the server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

---

## Running the tests

```bash
python manage.py test
```

83 tests cover every endpoint including its permission and status code
behaviour. A single app or module can be run on its own:

```bash
python manage.py test offers
python manage.py test accounts.tests.test_auth
```

---

## Environment variables

| Variable               | Required | Example                        | Purpose                                                        |
| ---------------------- | -------- | ------------------------------ | -------------------------------------------------------------- |
| `SECRET_KEY`           | yes      | `django-insecure-...`          | Django's cryptographic key. No default, the server needs it.    |
| `DEBUG`                | no       | `True`                         | Debug mode. Defaults to `False`; never enable it in production. |
| `ALLOWED_HOSTS`        | no       | `localhost,127.0.0.1`          | Comma-separated hostnames the server answers for.               |
| `CORS_ALLOWED_ORIGINS` | no       | `http://127.0.0.1:5500`        | Comma-separated origins the frontend may call the API from.     |

---

## Project layout

```
core/          Project configuration, root URLs and the base-info endpoint
accounts/      Custom user model, profiles, registration and login
offers/        Offers and their three package tiers
orders/        Orders placed by customers
reviews/       Customer reviews of business users
```

Each app keeps its API layer in a subpackage (`api/`, or `auth/` and `profile/`
in `accounts`) holding the serializers, views, permissions and URLs.

---

## Authentication

Registration and login both return a token. Send it with every request to a
protected endpoint:

```
Authorization: Token 83bf098723b08f7b23429u0fv8274
```

The token does not expire. Signing in again returns the same key.

Three endpoints are public: `POST /api/registration/`, `POST /api/login/` and
`GET /api/base-info/`. Everything else answers `401` without a valid token.

---

## User roles

Every account is either a **business** or a **customer** account, chosen at
registration and fixed afterwards.

| Action                     | Business | Customer | Staff |
| -------------------------- | -------- | -------- | ----- |
| Read offers, reviews, profiles | yes  | yes      | yes   |
| Create and edit own offers | yes      | no       | no    |
| Place orders               | no       | yes      | no    |
| Change an order's status   | own only | no       | no    |
| Delete orders              | no       | no       | yes   |
| Write reviews              | no       | yes      | no    |
| Edit or delete own review  | no       | yes      | no    |

---

## API reference

Base URL: `http://127.0.0.1:8000/api/`

### Authentication

#### `POST /api/registration/`

Creates an account and returns its token. Public.

Request:

```json
{
  "username": "exampleUsername",
  "email": "example@mail.de",
  "password": "examplePassword",
  "repeated_password": "examplePassword",
  "type": "customer"
}
```

Response `201`:

```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "username": "exampleUsername",
  "email": "example@mail.de",
  "user_id": 123
}
```

`400` when the passwords differ, the username or email is taken, `type` is
missing or the password fails Django's password validators.

#### `POST /api/login/`

Returns the token of an existing account. Public.

Request:

```json
{ "username": "exampleUsername", "password": "examplePassword" }
```

Response `200`: same body as registration. `400` for wrong credentials.

---

### Profiles

#### `GET /api/profile/{pk}/`

Full profile of one user. `pk` is the **user** id, not a separate profile id.
Empty fields come back as `""`, never as `null`.

Response `200`:

```json
{
  "user": 1,
  "username": "max_mustermann",
  "first_name": "Max",
  "last_name": "Mustermann",
  "file": "profile_picture.jpg",
  "location": "Berlin",
  "tel": "123456789",
  "description": "Business description",
  "working_hours": "9-17",
  "type": "business",
  "email": "max@business.de",
  "created_at": "2023-01-01T12:00:00Z"
}
```

`401` without a token, `404` for an unknown user.

#### `PATCH /api/profile/{pk}/`

Updates the own profile. Editable: `first_name`, `last_name`, `file`,
`location`, `tel`, `description`, `working_hours`, `email`.

`403` when editing someone else's profile, `400` when the email is already in
use.

#### `GET /api/profiles/business/`

Array of all business profiles. Not paginated.

#### `GET /api/profiles/customer/`

Array of all customer profiles, reduced to `user`, `username`, `first_name`,
`last_name`, `file` and `type`. Not paginated.

---

### Offers

An offer always has exactly three package tiers: `basic`, `standard` and
`premium`.

#### `GET /api/offers/`

Paginated list. Each entry carries `min_price` and `min_delivery_time` derived
from its tiers, links to those tiers, and a `user_details` block.

Query parameters:

| Parameter           | Type    | Effect                                             |
| ------------------- | ------- | -------------------------------------------------- |
| `creator_id`        | integer | Only offers of this business user.                 |
| `min_price`         | number  | Only offers priced at or above this value.         |
| `max_delivery_time` | integer | Only offers delivering within this many days.      |
| `ordering`          | string  | `updated_at` or `min_price`, prefix `-` to invert. |
| `search`            | string  | Matches title and description.                     |
| `page`              | integer | Page number.                                       |
| `page_size`         | integer | Results per page, default 6, maximum 100.          |

Response `200`:

```json
{
  "count": 1,
  "next": "http://127.0.0.1:8000/api/offers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "title": "Website Design",
      "image": null,
      "description": "Professional website design",
      "created_at": "2024-09-25T10:00:00Z",
      "updated_at": "2024-09-28T12:00:00Z",
      "details": [
        { "id": 1, "url": "http://127.0.0.1:8000/api/offerdetails/1/" },
        { "id": 2, "url": "http://127.0.0.1:8000/api/offerdetails/2/" },
        { "id": 3, "url": "http://127.0.0.1:8000/api/offerdetails/3/" }
      ],
      "min_price": 100,
      "min_delivery_time": 7,
      "user_details": {
        "first_name": "John",
        "last_name": "Doe",
        "username": "jdoe"
      }
    }
  ]
}
```

#### `POST /api/offers/`

Creates an offer. Business users only. All three tiers have to be present.

Request:

```json
{
  "title": "Grafikdesign-Paket",
  "image": null,
  "description": "A complete graphic design package.",
  "details": [
    {
      "title": "Basic Design",
      "revisions": 2,
      "delivery_time_in_days": 5,
      "price": 100,
      "features": ["Logo Design", "Visitenkarte"],
      "offer_type": "basic"
    },
    {
      "title": "Standard Design",
      "revisions": 5,
      "delivery_time_in_days": 7,
      "price": 200,
      "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
      "offer_type": "standard"
    },
    {
      "title": "Premium Design",
      "revisions": 10,
      "delivery_time_in_days": 10,
      "price": 500,
      "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
      "offer_type": "premium"
    }
  ]
}
```

Response `201`: the offer with all three tiers in full, each with its own id.
`400` for fewer than three tiers or a repeated `offer_type`, `403` for customer
accounts.

#### `GET /api/offers/{id}/`

One offer with links to its tiers. Same shape as a list entry, without
`user_details`.

#### `PATCH /api/offers/{id}/`

Updates the offer. Owner only. Tiers are matched by `offer_type`, so every tier
object in the payload has to carry it; the tier keeps its id.

```json
{
  "title": "Updated Grafikdesign-Paket",
  "details": [
    {
      "title": "Basic Design Updated",
      "revisions": 3,
      "delivery_time_in_days": 6,
      "price": 120,
      "features": ["Logo Design", "Flyer"],
      "offer_type": "basic"
    }
  ]
}
```

The response always contains all three tiers, not only the changed one. `403`
for anyone but the owner.

#### `DELETE /api/offers/{id}/`

Deletes the offer and its tiers. Owner only. `204` with an empty body.

#### `GET /api/offerdetails/{id}/`

One package tier with all of its fields.

```json
{
  "id": 1,
  "title": "Basic Design",
  "revisions": 2,
  "delivery_time_in_days": 5,
  "price": 100,
  "features": ["Logo Design", "Visitenkarte"],
  "offer_type": "basic"
}
```

---

### Orders

An order is a copy of the package tier at the time of booking. Editing the offer
afterwards does not change existing orders.

#### `GET /api/orders/`

Array of the orders the caller is party to, as customer or as business user. Not
paginated.

```json
[
  {
    "id": 1,
    "customer_user": 1,
    "business_user": 2,
    "title": "Logo Design",
    "revisions": 3,
    "delivery_time_in_days": 5,
    "price": 150,
    "features": ["Logo Design", "Visitenkarten"],
    "offer_type": "basic",
    "status": "in_progress",
    "created_at": "2024-09-29T10:00:00Z",
    "updated_at": "2024-09-30T12:00:00Z"
  }
]
```

#### `POST /api/orders/`

Places an order. Customer accounts only.

```json
{ "offer_detail_id": 1 }
```

Response `201`: the full order with status `in_progress`. `403` for business
accounts, `404` for an unknown `offer_detail_id`.

#### `PATCH /api/orders/{id}/`

Changes the status. Only the business user of that order may do this.

```json
{ "status": "completed" }
```

Allowed values: `in_progress`, `completed`, `cancelled`. Any other field in the
body is rejected with `400`. Response `200`: the full order.

#### `DELETE /api/orders/{id}/`

Deletes the order. Staff accounts only. `204` with an empty body.

#### `GET /api/order-count/{business_user_id}/`

Number of orders this business user has in progress.

```json
{ "order_count": 5 }
```

`404` when the id does not belong to a business user.

#### `GET /api/completed-order-count/{business_user_id}/`

Number of completed orders.

```json
{ "completed_order_count": 10 }
```

---

### Reviews

A customer can review a business user once.

#### `GET /api/reviews/`

Array of all reviews. Not paginated.

| Parameter          | Type    | Effect                                        |
| ------------------ | ------- | --------------------------------------------- |
| `business_user_id` | integer | Only reviews about this business user.        |
| `reviewer_id`      | integer | Only reviews written by this user.            |
| `ordering`         | string  | `updated_at` or `rating`, prefix `-` to invert. |

```json
[
  {
    "id": 1,
    "business_user": 2,
    "reviewer": 3,
    "rating": 4,
    "description": "Sehr professioneller Service.",
    "created_at": "2023-10-30T10:00:00Z",
    "updated_at": "2023-10-31T10:00:00Z"
  }
]
```

#### `POST /api/reviews/`

Creates a review. Customer accounts only. `reviewer` is taken from the token and
cannot be set in the body.

```json
{ "business_user": 2, "rating": 4, "description": "Alles war toll!" }
```

`rating` has to be between 1 and 5. `403` for business accounts, `400` for a
second review about the same business user, a rating out of range, or a
`business_user` that is not a business account.

#### `PATCH /api/reviews/{id}/`

Updates `rating` and `description`. Author only. Any other field in the body is
rejected with `400`. Response `200`: the full review.

#### `DELETE /api/reviews/{id}/`

Deletes the review. Author only. `204` with an empty body.

---

### Platform statistics

#### `GET /api/base-info/`

Aggregated numbers for the landing page. Public.

```json
{
  "review_count": 10,
  "average_rating": 4.6,
  "business_profile_count": 45,
  "offer_count": 150
}
```

`average_rating` is rounded to one decimal place and is `0.0` while there are no
reviews.

---

## Troubleshooting

**`django.core.exceptions.ImproperlyConfigured: Set the SECRET_KEY environment
variable`** — the `.env` file is missing or has no `SECRET_KEY`. See step 4.

**`no such table: accounts_user`** — the migrations have not been applied. Run
`makemigrations` and `migrate` from step 5.

**The frontend loads but every request fails** — the origin the frontend is
served from is not in `CORS_ALLOWED_ORIGINS`. The value has to match protocol,
host and port exactly.

**`401 Unauthorized` on an endpoint that should work** — the header has to read
`Authorization: Token <key>`, with the word `Token`, not `Bearer`.

**`ModuleNotFoundError` after installing** — the virtual environment is not
active. Activate it again as described in step 2.
