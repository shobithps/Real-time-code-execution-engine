from kafka import KafkaConsumer
import requests
import json
import logging
import subprocess
import tempfile
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pythonConsumer")

consumer = KafkaConsumer(
    "python",
    bootstrap_servers=["kafka:9092"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    key_deserializer=lambda k: k.decode("utf-8") if k else None,
    group_id="python-consumer-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

API_URL = "http://producer:8000/submit-result"  # producer service in docker-compose

def run_python_code(code: str, input_data: str = ""):
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = os.path.join(tmpdir, "main.py")
        with open(py_file, "w") as f:
            f.write(code)

        try:
            run_result = subprocess.run(
                ["python3", py_file],
                input=input_data if isinstance(input_data, str) else input_data.decode(),
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
                "returncode": run_result.returncode
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}


logger.info("Python Consumer started. Listening for messages...")

for message in consumer:
    data = message.value
    logger.info(f"Received: {data}")

    result = run_python_code(data["code"], data.get("input_data", ""))

    payload = {
        "request_id": data["request_id"],
        "language": "python",
        "output": result,
        "status": "completed"
    }

    try:
        res = requests.post(API_URL, json=payload)
        logger.info(f"Result sent: {res.status_code} {res.text}")
    except Exception as e:
        logger.error(f"Failed to POST result: {e}")
