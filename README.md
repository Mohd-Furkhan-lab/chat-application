# Chat Application Backend

A real-time chat backend built with **FastAPI**, **PostgreSQL**, **Redis**, **Cloudinary** and **WebSockets**. It supports private one-to-one chats, public and private group chats with admin controls, photo/video/audio/document sharing, profile pictures, and secure cookie-based JWT authentication.

> Companion frontend: [`chat_applciation_v2`](https://github.com/Mohd-Furkhan-lab/chat_applciation_v2) (live at https://chat-applciation-v2.vercel.app).

---

## Features

**Authentication**
- Email + password signup and login (bcrypt-hashed passwords)
- JWT access and refresh tokens delivered as cookies, with silent token refresh
- Logout that revokes tokens (Redis blacklist for access tokens, PostgreSQL for refresh tokens)
- Auto-generated unique usernames such as `Brave_Wolf`
- Profile picture upload

**Direct messages**
- Add contacts and start one-to-one conversations
- Text and media messages (image, video, audio, documents)
- Message history and clear-conversation support
- Instant delivery over WebSocket when the recipient is online

**Group chats**
- Create **public** or **private** groups
- Public groups can be joined by anyone; private groups are invite-only (admin adds members)
- Group text and media messages broadcast live to everyone connected
- Group history available to members

**Group administration**
- Admin-only endpoints for viewing members and group info
- Add or remove members, change member roles, upload a group picture, delete a group
- Role-based access enforced through a reusable `is_admin` dependency

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI + Uvicorn |
| Database / ORM | PostgreSQL (`psycopg2`) + SQLAlchemy 2.0 |
| Cache / token blacklist | Redis |
| Media storage | Cloudinary |
| Auth | PyJWT (HS256) + bcrypt |
| Validation | Pydantic v2 (`EmailStr`) |
| Real-time | WebSockets |
| Testing | pytest, pytest-asyncio |

## Project Structure

```text
chat-application/
├── app/
│   └── main.py                    # FastAPI app, registers all routers
├── auth/
│   └── jwt_token.py               # create / verify / refresh JWTs
├── config/
│   ├── database.py                # SQLAlchemy engine, session factory, base
│   ├── redis.py                   # Redis client
│   └── cloudinary.py              # Cloudinary configuration
├── connection_manager/
│   ├── user_connection.py         # active WebSockets for direct chats
│   └── group_connection.py        # active WebSockets per group
├── dependencies/
│   ├── user_payload.py            # get_current_user (reads the access cookie)
│   └── admin.py                   # is_admin (group admin guard)
├── models/
│   ├── users.py
│   ├── conversation.py
│   ├── messages.py
│   ├── group_chat.py
│   ├── group_memebers.py
│   ├── group_msg.py
│   └── token_blacklist.py
├── routes/
│   ├── user.py                    # /users
│   ├── chats.py                   # /chat
│   ├── groups.py                  # /groups
│   ├── group_admin.py             # /admin
│   └── websockets.py              # /ws
├── schemas/
│   ├── user_schemas.py
│   ├── group_schmeas.py
│   └── group_admin_schema.py
├── services/
│   ├── user_services.py
│   ├── chats_services.py
│   ├── group_services.py
│   ├── group_msg_services.py
│   └── admin_services.py
├── tests/                         # pytest suites for the service layer
├── utlis/
│   ├── username_generator.py      # random "Title_Animal" usernames
│   └── media_types.py             # MediaType enum
├── run.py                         # entrypoint: creates tables, adds CORS, exposes `app`
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python **3.12+** (the code uses `datetime.UTC` and nested same-type quotes in f-strings)
- A running **PostgreSQL** database
- A running **Redis** instance
- A free **Cloudinary** account (for media and profile pictures)

### 1. Clone

```bash
git clone https://github.com/Mohd-Furkhan-lab/chat-application.git
cd chat-application
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root (it is git-ignored). Names are **lowercase** and case-sensitive:

```env
secret_key=replace_with_a_long_random_string
database_url=postgresql://username:password@localhost:5432/chat_db
redis_url=redis://localhost:6379/0
cloudinary_name=your_cloud_name
cloudinary_key=your_api_key
cloudinary_secret=your_api_secret
```

| Variable | Purpose |
|---|---|
| `secret_key` | Signing key for JWTs (HS256). Use a long random value. |
| `database_url` | SQLAlchemy connection string for PostgreSQL. |
| `redis_url` | Redis connection string, used for the access-token blacklist. |
| `cloudinary_name`, `cloudinary_key`, `cloudinary_secret` | Cloudinary credentials for media uploads. |

> These are read at import time, so the app will not start if any are missing.

### 4. Run

```bash
uvicorn run:app --reload
```

The server starts at `http://127.0.0.1:8000`. Tables (`users`, `convo`, `msg`, `groups`, `members`, `group_msg`, `revoked_tokens`) are created automatically on startup via `BaseModel.metadata.create_all(engine)`.

Interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Authentication

Authentication is **cookie-based**. A successful login sets two cookies:

| Cookie | Type | Lifetime |
|---|---|---|
| `access` | JWT (`type: access`) | 3 days |
| `refresh` | JWT (`type: refresh`) | 3 days |

Each token carries `user_id`, `user_name`, a unique `jti`, a `type` and an `exp`. Cookies use `Secure` and `SameSite=None` so they work with a frontend on a different domain, which means the API should be served over HTTPS (browsers generally treat `localhost` as secure for local development).

Protected routes read the `access` cookie through the `get_current_user` dependency.

**Logout:** the access token's `jti` is written to Redis with a TTL equal to its remaining lifetime, the refresh token's `jti` is stored in the `revoked_tokens` table, both cookies are deleted, and the user's WebSocket is closed.

## API Reference

All endpoints except signup and login require a valid `access` cookie.

### Users: `/users`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/users/signup` | Register with `email` and `password`. A random username is assigned and returned. |
| `POST` | `/users/login` | Log in. Sets the `access` and `refresh` cookies. |
| `GET` | `/users/me` | Current user's `user_name`, `email` and `profile_pic`. |
| `POST` | `/users/profile-pic/upload` | Upload a profile picture (multipart, field `file`). |
| `POST` | `/users/refresh` | Issue a new `access` cookie from the `refresh` cookie. |
| `POST` | `/users/logout` | Revoke both tokens and clear cookies. |

```json
{ "email": "user@example.com", "password": "your-password" }
```

### Direct chats: `/chat`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/chat/contacts` | List contacts as `{ username, pfp }` objects. |
| `POST` | `/chat/{username}` | Start a conversation with an existing user. |
| `GET` | `/chat/{username}` | Message history with that user (text and media). |
| `POST` | `/chat/send-msg` | Send a text message: `{ "to": "Brave_Wolf", "msg": "Hi!" }`. |
| `POST` | `/chat/send-media` | Send media (multipart: `to` form field + `file`). |
| `DELETE` | `/chat/clear-chat/{username}` | Delete the conversation and its messages. |

A conversation must exist before messages can be sent. If the recipient is offline the message is still stored and the response says `"user offline"`.

### Groups: `/groups`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/groups/` | Names of groups you have joined. |
| `POST` | `/groups/` | Create a group: `{ "gname": "team", "type": "public" }`. The creator becomes admin. |
| `PUT` | `/groups/` | Change group type (admin only): `{ "gname": "team", "new_type": "private" }`. |
| `GET` | `/groups/{groupname}` | Group details (members only). |
| `POST` | `/groups/members/{groupname}` | Join a **public** group. |
| `GET` | `/groups/{groupname}/chat` | Group message history (members only). |
| `POST` | `/groups/{groupname}/chat` | Send a text message: `{ "msg": "Hello team" }`. |
| `POST` | `/groups/{groupname}/media` | Send media (multipart, field `file`). |

### Group admin: `/admin`

All endpoints require you to be an **admin** of the group.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/{groupname}/members` | List members and join dates. |
| `GET` | `/admin/{groupname}/info` | Group metadata. |
| `POST` | `/admin/{groupname}/members` | Add a member: `{ "username": "...", "role": "member" }`. |
| `PUT` | `/admin/{groupname}/members/role` | Change a member's role: `{ "username": "...", "new_role": "admin" }`. |
| `DELETE` | `/admin/{groupname}/members/{username}` | Remove a member. |
| `POST` | `/admin/{groupname}/profile-pic` | Upload a group picture (multipart, field `file`). |
| `DELETE` | `/admin/{groupname}` | Delete the group. |

### Media

Uploads are sent to Cloudinary and the secure URL is stored with the message. Supported types are determined by the file's MIME prefix:

| MIME prefix | Stored as |
|---|---|
| `image/*` | `image` |
| `video/*` | `video` |
| `audio/*` | `audio` |
| `application/*` | `application` (documents) |

Anything else is rejected with `400 Unsupported media type`.

### WebSockets: `/ws`

| Endpoint | Purpose |
|---|---|
| `ws://<host>/ws/connect` | Receive direct messages in real time. |
| `ws://<host>/ws/connect/{groupname}` | Receive messages for a specific group in real time. |

Both read the `access` cookie from the handshake to identify the user. Messages are **sent** through the REST endpoints above; WebSockets are the delivery channel.

Payloads pushed to clients:

```json
// direct message
{ "from": "Swift_Fox", "message": "Hey!" }

// group message
{ "sender": "Swift_Fox", "msg": "Hello team" }
```

For media messages, the message text is the Cloudinary URL.

## Data Model

| Table | Key columns |
|---|---|
| `users` | `user_id` (PK), `user_name` (unique), `email`, `password` (bcrypt hash), `profile_pic` |
| `convo` | `convo_id` (PK), `user1`, `user2` (usernames, stored sorted) |
| `msg` | `msg_id` (PK), `convo_id` (FK, cascade), `msg`, `sender`, `media_url`, `media_type`, `timestamp` |
| `groups` | `group_id` (PK), `group_name` (unique), `created_by` (FK), `created_at`, `no_of_members`, `group_pfp`, `type` (`public` / `private`) |
| `members` | `member_id` (PK), `user_id` (FK), `group_id` (FK), `role`, `joined_at` |
| `group_msg` | `msg_id` (PK), `group_id` (FK, cascade), `sender`, `msg`, `media_url`, `media_type`, `timestamp` |
| `revoked_tokens` | `id` (PK), `jti`, `expires_at`, `revoked` |

## Testing

```bash
pytest
```

Test suites in `tests/` cover the user, chat, group, group-message and admin service layers. Because service modules read their configuration at import time, make sure the environment variables above are available (for example via `.env`) before running.

## CORS

`run.py` allows credentialed requests from:

- `http://localhost:3000`, `3001`, `5500` and the matching `127.0.0.1` origins
- `https://chat-frontend-gilt-phi.vercel.app`
- `https://chat-applciation-v2.vercel.app`

Add your own frontend origin to `allow_origins` in `run.py` when deploying elsewhere.

## Contributing

Issues and pull requests are welcome. Please create a feature branch, describe the change clearly, and include or update tests where it makes sense.

## License

No license file is included yet. Add one (for example MIT) to define how others may use this code.
