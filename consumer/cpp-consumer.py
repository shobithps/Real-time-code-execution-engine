from kafka import KafkaConsumer
import requests
import json
import logging
import subprocess
import tempfile
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cppConsumer")

consumer = KafkaConsumer(
    "cpp",
    bootstrap_servers=["kafka:9092"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    key_deserializer=lambda k: k.decode("utf-8") if k else None,
    group_id="cpp-consumer-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

API_URL = "http://producer:8000/submit-result"  # producer service in docker-compose

def run_cpp_code(code: str, input_data: str = ""):
    with tempfile.TemporaryDirectory() as tmpdir:
        cpp_file = os.path.join(tmpdir, "main.cpp")
        exe_file = os.path.join(tmpdir, "main.out")

        with open(cpp_file, "w") as f:
            f.write(code)

        try:
            # Compile C++ code
            compile_result = subprocess.run(
                ["g++", cpp_file, "-o", exe_file],
                capture_output=True,
                text=True
            )
            if compile_result.returncode != 0:
                return {"stdout": "", "stderr": compile_result.stderr, "returncode": compile_result.returncode}

            # Run compiled binary
            run_result = subprocess.run(
                [exe_file],
                input=input_data if isinstance(input_data, str) else input_data.decode(),
                capture_output=True,
                text=True,
                timeout=5
            )
            return {"stdout": run_result.stdout, "stderr": run_result.stderr, "returncode": run_result.returncode}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}


logger.info("C++ Consumer started. Listening for messages...")

for message in consumer:
    data = message.value
    logger.info(f"Received: {data}")

    result = run_cpp_code(data["code"], data.get("input_data", ""))

    payload = {
        "request_id": data["request_id"],
        "language": "cpp",
        "output": result,
        "status": "completed"
    }

    try:
        res = requests.post(API_URL, json=payload)
        logger.info(f"Result sent: {res.status_code} {res.text}")
    except Exception as e:
        logger.error(f"Failed to POST result: {e}")
