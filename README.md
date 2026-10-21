# Chat Application

A FastAPI-based backend for a real-time chat application with user authentication, JWT-based sessions, PostgreSQL persistence, and WebSocket communication.

This project provides the server-side foundation for a chat platform and is designed to work with a frontend client.

## Features

- User signup and login
- JWT access and refresh token support
- Cookie-based authentication
- Real-time messaging using WebSockets
- Conversation management APIs
- PostgreSQL integration with SQLAlchemy
- Modular backend structure for easier extension

## Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT (PyJWT)
- Redis
- WebSockets
- Uvicorn

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
├── utlis/
├── .gitignore
├── requirements.txt
├── run.py
├── README.md
└── .env
```

## Prerequisites

- Python 3.10+
- PostgreSQL running locally or remotely
- Virtual environment tool like `venv`
- `.env` file with project configuration

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_super_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/chat_db
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Mohd-Furkhan-lab/chat-application.git
cd chat-application
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the `.env` file.

## Running the Application

Start the FastAPI app with:

```bash
uvicorn run:app --reload
```

## API Overview

### User Routes

- `POST /users/signup` — Register a new user
- `POST /users/login` — Log in and receive auth cookies
- `GET /users/me` — Get current authenticated user
- `POST /users/refresh` — Generate a new access token
- `POST /users/logout` — Log the user out

### Chat Routes

- `GET /chat/contacts` — Get contacts
- `POST /chat/send-msg` — Send a message
- `GET /chat/{username}` — Get conversation history
- `POST /chat/{username}` — Add a user to a conversation
- `DELETE /chat/clear-chat/{username}` — Clear a conversation

### WebSocket Route

- `ws://<host>/ws/connect` — Real-time chat connection

## Notes

- The app automatically creates database tables at startup with SQLAlchemy.
- Authentication is currently cookie and JWT based.
- This repo is intended to be paired with a frontend client for the full chat experience.

## Contributing

Contributions are welcome. Please create a feature branch and submit a pull request with a clear summary of your changes.

## License

This project does not currently include a license file. Add one if you want to define usage and distribution terms.
