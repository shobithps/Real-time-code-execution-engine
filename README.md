# Real-time-code-execution-engine
A distributed system to write and run Python, Java, and C++ from a web editor. Built with React, FastAPI, Kafka, Redis, and Docker, it uses a producer–consumer model where code is queued, executed in Dockerized consumers, and results stored in Redis. Supports 500–1000 users with real-time, sub-second outputs.
