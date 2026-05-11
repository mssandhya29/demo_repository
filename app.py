"""
Object Counter - Python Backend (Flask)
=======================================
Receives two images (reference object + scene) via POST /count
and returns a JSON count using Claude's vision API.

Requirements:
    pip install flask anthropic flask-cors pillow

Usage:
    1. Set your API key:
          export ANTHROPIC_API_KEY=sk-ant-...
       Or create a .env file with ANTHROPIC_API_KEY=sk-ant-...

    2. Run the server:
          python app.py

    3. Open index.html in a browser, switch to "Python Backend" mode.
"""

import os
import json
import base64
import anthropic
import uuid
from datetime import datetime

import httpx
import certifi

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from the HTML frontend
@app.route("/")
def index():
    return send_from_directory(".", "index.html")
# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

MODEL = "claude-opus-4-5"
MAX_IMAGE_DIMENSION = 1568  # Resize large images to stay within API limits


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resize_image(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    """Resize image if it exceeds MAX_IMAGE_DIMENSION on either side."""
    img = Image.open(io.BytesIO(image_bytes))

    # Convert RGBA/palette images to RGB for JPEG compatibility
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        mime_type = "image/jpeg"

    w, h = img.size
    if max(w, h) > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    fmt = "JPEG" if "jpeg" in mime_type or "jpg" in mime_type else "PNG"
    img.save(buf, format=fmt)
    return buf.getvalue(), mime_type


def to_base64(image_bytes: bytes) -> str:
    return base64.standard_b64encode(image_bytes).decode("utf-8")


def count_objects_with_claude(
    ref_bytes: bytes, ref_mime: str,
    scene_bytes: bytes, scene_mime: str
) -> dict:
    """Call Claude vision API and return structured count result."""
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, http_client=httpx.Client(verify=False))

    # Resize images to avoid token/size limits
    ref_bytes, ref_mime = resize_image(ref_bytes, ref_mime)
    scene_bytes, scene_mime = resize_image(scene_bytes, scene_mime)

    prompt = (
        "The first image is a reference object. "
        "The second image is a scene. "
        "Count how many instances of the reference object appear in the scene. "
        "Respond ONLY with valid JSON — no markdown, no explanation:\n"
        '{"count": <integer>, "object_name": "<short name of the object>", '
        '"confidence": "high|medium|low", "notes": "<one brief sentence>"}'
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": ref_mime,
                            "data": to_base64(ref_bytes),
                        },
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": scene_mime,
                            "data": to_base64(scene_bytes),
                        },
                    },
                ],
            }
        ],
    )

    raw = "".join(
        block.text for block in message.content if block.type == "text"
    )
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """Health check — useful for debugging."""
    return jsonify({"status": "ok", "model": MODEL})


@app.route("/count", methods=["POST"])
def count():
    """
    POST /count
    Form fields:
        reference  - image file (the reference object)
        scene      - image file (the scene to search)
    Returns:
        {"count": int, "object_name": str, "confidence": str, "notes": str}
    """
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "ANTHROPIC_API_KEY not set on the server."}), 500

    if "reference" not in request.files or "scene" not in request.files:
        return jsonify({"error": "Both 'reference' and 'scene' image files are required."}), 400

    ref_file = request.files["reference"]
    scene_file = request.files["scene"]

    ref_bytes = ref_file.read()
    scene_bytes = scene_file.read()

    ref_mime = ref_file.mimetype or "image/jpeg"
    scene_mime = scene_file.mimetype or "image/jpeg"

    if not ref_bytes or not scene_bytes:
        return jsonify({"error": "One or both uploaded files are empty."}), 400

    try:
        result = count_objects_with_claude(ref_bytes, ref_mime, scene_bytes, scene_mime)
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Claude returned non-JSON response: {e}"}), 500
    except anthropic.APIError as e:
        return jsonify({"error": f"Anthropic API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Leave Request helpers
# ---------------------------------------------------------------------------

LEAVE_REQUESTS_FILE = os.path.join(os.path.dirname(__file__), "leave_requests.json")


def load_leave_requests() -> list:
    if not os.path.exists(LEAVE_REQUESTS_FILE):
        return []
    with open(LEAVE_REQUESTS_FILE, "r") as f:
        return json.load(f)


def save_leave_requests(requests: list) -> None:
    with open(LEAVE_REQUESTS_FILE, "w") as f:
        json.dump(requests, f, indent=2)


# ---------------------------------------------------------------------------
# Leave Request routes
# ---------------------------------------------------------------------------

@app.route("/leave", methods=["GET"])
def leave_page():
    return send_from_directory(".", "leave.html")


@app.route("/api/leaves", methods=["GET"])
def list_leaves():
    return jsonify(load_leave_requests())


@app.route("/api/leaves", methods=["POST"])
def submit_leave():
    data = request.get_json(force=True)
    required = {"employee_name", "start_date", "end_date"}
    if not required.issubset(data):
        return jsonify({"error": f"Missing fields: {required - data.keys()}"}), 400

    leave = {
        "id": str(uuid.uuid4()),
        "employee_name": data["employee_name"],
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "reason": data.get("reason", ""),
        "status": data.get("status", "Pending"),
        "submitted_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    requests_list = load_leave_requests()
    requests_list.append(leave)
    save_leave_requests(requests_list)
    return jsonify(leave), 201


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not ANTHROPIC_API_KEY:
        print("⚠️  WARNING: ANTHROPIC_API_KEY is not set.")
        print("   Export it: export ANTHROPIC_API_KEY=sk-ant-...")

    print(f"✅  Starting Object Counter server on http://localhost:5000")
    print("ANTHROPIC_API_KEY loaded:", bool(os.environ.get("ANTHROPIC_API_KEY")))
    app.run(debug=True, port=5000)
