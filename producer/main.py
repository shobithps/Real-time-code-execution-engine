from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import logging
from typing import Optional
import uvicorn
from datetime import datetime
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Code Execution API with Kafka", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kafka setup
KAFKA_BOOTSTRAP_SERVERS = ["kafka:9092"]
topic_map = {
    "python": "python",
    "java": "java",
    "cpp": "cpp"
}

producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                api_version=(2, 0, 2)
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Kafka init failed: {e}")
            raise HTTPException(status_code=500, detail="Kafka connection failed")
    return producer

# Redis setup
redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

class CodeRequest(BaseModel):
    code: str
    language: str
    input_data: str = ""
    user_id: Optional[str] = None

class CodeResponse(BaseModel):
    message: str
    request_id: str
    status: str
    timestamp: str

class CodeResult(BaseModel):
    request_id: str
    language: str
    output: dict
    status: str

@app.on_event("startup")
async def startup_event():
    get_kafka_producer()
    logger.info("FastAPI app started")

@app.on_event("shutdown")
async def shutdown_event():
    global producer
    if producer:
        producer.close()
        logger.info("Kafka producer closed")

@app.post("/submit-code", response_model=CodeResponse)
async def submit_code(request: CodeRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    try:
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        timestamp = datetime.now().isoformat()

        topic = topic_map.get(request.language.lower())
        if not topic:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {request.language}")

        kafka_message = {
            "request_id": request_id,
            "code": request.code,
            "language": request.language,
            "input_data": request.input_data,
            "user_id": request.user_id,
            "timestamp": timestamp,
            "status": "submitted"
        }

        kafka_producer = get_kafka_producer()
        kafka_producer.send(topic=topic, key=request_id, value=kafka_message)

        # Store pending status in Redis
        redis_client.set(request_id, json.dumps({"status": "queued"}))

        return CodeResponse(
            message="Code submitted successfully to processing queue",
            request_id=request_id,
            status="queued",
            timestamp=timestamp
        )
    except Exception as e:
        logger.error(f"Submit failed: {e}")
        raise HTTPException(status_code=500, detail="Kafka send failed")

@app.post("/submit-result")
async def submit_result(result: CodeResult):
    redis_client.set(result.request_id, json.dumps(result.dict()))
    return {"message": "Result stored in Redis"}

@app.get("/get-result/{request_id}")
async def get_result(request_id: str):
    result = redis_client.get(request_id)
    if not result:
        return {"status": "pending", "output": None}
    return json.loads(result)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
