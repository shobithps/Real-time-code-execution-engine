# Real-time-code-execution-engine
A distributed system to write and run Python, Java, and C++ from a web editor. Built with React, FastAPI, Kafka, Redis, and Docker, it uses a producer–consumer model where code is queued, executed in Dockerized consumers, and results stored in Redis. Supports 500–1000 users with real-time, sub-second outputs.

---

## 🚀 Features
- Write and run code in real time.
- Supports multiple languages (Python, Java, C++).
- Backend powered by FastAPI, Kafka, and Redis for scalable execution.
- Frontend built with React for a smooth developer experience.
- Fully containerized with Docker.

---

## 🛠️ Getting Started

### 1. Run the frontend
Navigate to the frontend directory and start the development server:
```bash
cd frontend
npm run dev
```

## 2. Run the backend with Docker

Open another terminal in the root project directory and run:

```bash
docker compose up --build
```

This will spin up all the necessary backend services.
