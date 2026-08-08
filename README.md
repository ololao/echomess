# ECHOMESSS ✰

## ABOUT ECHOMESSS

EchoMess is a lightweight, real-time messaging application built around WebSockets. Users register with an email address, confirm it via a link, and then create or join persistent chat rooms where messages are delivered instantly. A short confirmation code is sent on each login for an extra layer of verification. The interface is fully responsive and works equally well on desktop and mobile browsers, with a one-click switch between light and dark themes.

## INTERNAL IMPLEMENTATION
On the backend, EchoMess runs on **FastAPI** served by **Gunicorn** with **Uvicorn** workers. Authentication uses **JWT** access and refresh tokens, with the refresh token stored in an HTTP-only cookie. **PostgreSQL** holds users, rooms, and message history, while **Redis** powers an in-memory pub/sub layer that fans messages out to every connected client and lets the service scale horizontally across multiple workers. A background worker task is spawned per active room and torn down once the last participant leaves, so idle rooms consume no resources. **Resend** handles transactional email (confirmation links and login codes), and **Loguru** provides structured logging throughout.

# TECHNOLOGY STACK 

- docker & docker-compose
- redis
- postgres
- python
- fastapi
- loguru
- alembic
- gunicorn & uvicorn
- resend for emails
- JWT authentication & authorization

# INSTALLATION

```bash
git clone https://github.com/ololao/echomess.git # clone repo
cd echomess #
docker compose up -d --build # run docker 

# how can I install docker? -> https://docs.docker.com/
```
