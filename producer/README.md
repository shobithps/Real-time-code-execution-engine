# FastAPI Backend with Kafka Producer

A FastAPI backend service that receives code from the frontend and sends it to a Kafka broker for processing.

## Features

- **FastAPI REST API**: Clean endpoints for code submission
- **Kafka Producer**: Sends code execution requests to Kafka broker
- **CORS Enabled**: Ready for frontend integration
- **Health Monitoring**: Service and Kafka connection health checks
- **Request Tracking**: Unique request IDs for message tracking
- **Error Handling**: Comprehensive error reporting

## Prerequisites

1. **Kafka Broker**: Make sure Kafka is running on `localhost:9092`
2. **Python 3.8+**: Required for FastAPI and Kafka client

### Setting up Kafka (if not already running)

**Using Docker:**
```bash
# Start Zookeeper
docker run -d --name zookeeper -p 2181:2181 confluentinc/cp-zookeeper:latest

# Start Kafka
docker run -d --name kafka -p 9092:9092 \
  --link zookeeper \
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  confluentinc/cp-kafka:latest
```

**Using Kafka directly:**
```bash
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Submit Code for Processing
**POST** `/submit-code`

Request body:
```json
{
  "code": "print('Hello, World!')",
  "language": "python",
  "input_data": "",
  "user_id": "user123"
}
```

Response:
```json
{
  "message": "Code submitted successfully to processing queue",
  "request_id": "req_20241201_143022_123456",
  "status": "queued",
  "timestamp": "2024-12-01T14:30:22.123456"
}
```

### Health Check
**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "message": "FastAPI server and Kafka connection are working",
  "kafka_broker": "localhost:9092",
  "kafka_topic": "code-execution"
}
```

### Kafka Status
**GET** `/kafka-status`

Response:
```json
{
  "status": "connected",
  "bootstrap_servers": ["localhost:9092"],
  "topic": "code-execution",
  "producer_config": {
    "acks": "all",
    "retries": 3,
    "api_version": "2.0.2"
  }
}
```

### Supported Languages
**GET** `/supported-languages`

Response:
```json
{
  "languages": [
    {"name": "Python", "value": "python", "extension": ".py"},
    {"name": "JavaScript", "value": "javascript", "extension": ".js"},
    {"name": "Java", "value": "java", "extension": ".java"},
    {"name": "C++", "value": "cpp", "extension": ".cpp"},
    {"name": "Go", "value": "go", "extension": ".go"},
    {"name": "Rust", "value": "rust", "extension": ".rs"}
  ]
}
```

## Kafka Message Format

Messages sent to the Kafka topic `code-execution` have this structure:

```json
{
  "request_id": "req_20241201_143022_123456",
  "code": "print('Hello, World!')",
  "language": "python",
  "input_data": "",
  "user_id": "user123",
  "timestamp": "2024-12-01T14:30:22.123456",
  "status": "submitted"
}
```

## Configuration

You can modify these settings in `main.py`:

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `KAFKA_TOPIC`: Topic name for code execution messages
- Producer settings: `acks`, `retries`, `retry_backoff_ms`, etc.

## Error Handling

The API handles various error scenarios:
- Empty code submission (400 Bad Request)
- Kafka connection failures (500 Internal Server Error)
- Message sending timeouts (500 Internal Server Error)

## Monitoring

Use the health check endpoints to monitor:
- FastAPI server status
- Kafka broker connectivity
- Producer configuration

## Usage with Frontend

Update your Next.js frontend to use the new endpoint:

```javascript
const submitCode = async (code, language) => {
  try {
    const response = await fetch('http://localhost:8000/submit-code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: code,
        language: language,
        input_data: '',
        user_id: 'frontend-user'
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Code submission failed:', error);
    return { message: error.message, status: 'error' };
  }
};
```