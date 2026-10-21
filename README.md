# Chat Application Backend

A FastAPI-based real-time chat backend with user authentication, JWT-based session management, PostgreSQL persistence, and WebSocket chat connectivity.

## Features

- User signup, login, logout, and token refresh
- JWT access and refresh tokens
- Protected chat routes
- WebSocket connection support for real-time messaging
- PostgreSQL database integration using SQLAlchemy
- Conversation/contact management APIs
- Redis and async-ready backend dependencies for scalable messaging workflows

## Project Structure

```text
chat-application/
├── app/
│   └── main.py
├── auth/
│   └── jwt_token.py
├── connection_manager/
│   └── manage_connection.py
├── db/
│   └── database.py
├── models/
│   ├── conversation.py
│   ├── messages.py
│   └── users.py
├── routes/
│   ├── chats.py
│   ├── user.py
│   └── websockets.py
├── schemas/
│   └── user_schemas.py
├── services/
│   ├── chats_services.py
│   └── user_services.py
├── tests/
├── utils/
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT (PyJWT)
- WebSockets
- Redis
- Uvicorn

## Prerequisites

- Python 3.10+
- PostgreSQL database
- Virtual environment tool such as `venv`
- Environment variables configured in a `.env` file

## Environment Variables

Create a `.env` file in the project root with values similar to:

```env
secret_key=your_super_secret_key
database_url=postgresql://username:password@host:5432/chat_db
```

> The application reads `secret_key` for JWT signing and `database_url` for the SQLAlchemy database connection.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Mohd-Furkhan-lab/chat-application.git
cd chat-application
git checkout backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Linux/macOS
# or
venv\Scripts\activate      # On Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your `.env` file and ensure the database is available.

## Running the Application

Start the server with:

```bash
uvicorn run:app --reload
```

The app exposes the FastAPI instance created in `run.py` and includes routers for users, chat APIs, and WebSocket routes.

## API Overview

### User Endpoints

- `POST /users/signup` — register a new user
- `POST /users/login` — log in and receive auth cookies
- `GET /users/me` — fetch authenticated user info
- `POST /users/refresh` — refresh access token
- `POST /users/logout` — clear session cookies

### Chat Endpoints

- `GET /chat/contacts` — fetch user's contacts
- `POST /chat/send-msg` — send a message
- `GET /chat/{username}` — get chat history with a user
- `POST /chat/{username}` — add a user to a conversation
- `DELETE /chat/clear-chat/{username}` — clear a conversation

### WebSocket Endpoint

- `ws://host/ws/connect` — real-time chat connection

## Notes

- Auth is cookie-based for the current implementation and expects `access` and `refresh` tokens to be sent in cookies.
- Database schema is created automatically when the app boots via `BaseModel.metadata.create_all(engine)` in `run.py`.
- This repository appears to be focused on the backend service for a chat application and is intended to be paired with a frontend client.

## License

This project does not currently include a license file. Add one if you want to define usage and distribution terms.

## Contributing

Contributions are welcome. If you'd like to improve the backend, open a pull request with a clear description of the change and any relevant tests.
