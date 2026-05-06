"""
Appian MCP Server for Claude Code
Connects Claude Code to Appian via natural language.

Tools exposed:
  - deploy_sail_interface     : Package SAIL code and deploy to Appian
  - get_deployment_status     : Check status of a deployment
  - query_records             : Query Appian records
  - create_record             : Create a new record
  - update_record             : Update an existing record
  - delete_record             : Delete a record
  - call_web_api              : Call any custom Appian Web API
  - start_process             : Start an Appian process model
  - get_process_status        : Get process instance status

Setup:
  pip install fastmcp requests
  export APPIAN_BASE_URL="https://your-instance.appiancloud.com/suite"
  export APPIAN_API_KEY="your-service-account-api-key"
  python appian_mcp_server.py
"""

import io
import json
import os
import uuid
import zipfile

import requests
from fastmcp import FastMCP

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
APPIAN_BASE_URL = os.environ.get("APPIAN_BASE_URL", "").rstrip("/")
APPIAN_API_KEY  = os.environ.get("APPIAN_API_KEY", "")

if not APPIAN_BASE_URL:
    raise EnvironmentError("APPIAN_BASE_URL is not set. Export it before starting the server.")
if not APPIAN_API_KEY:
    raise EnvironmentError("APPIAN_API_KEY is not set. Export it before starting the server.")

SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"Appian {APPIAN_API_KEY}",
    "Accept":        "application/json",
})

mcp = FastMCP("appian-server")


# ──────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────

def _get(endpoint: str, **kwargs) -> dict:
    url = f"{APPIAN_BASE_URL}{endpoint}"
    r = SESSION.get(url, timeout=30, **kwargs)
    r.raise_for_status()
    return r.json()


def _post(endpoint: str, json_body: dict = None, files=None, **kwargs) -> dict:
    url = f"{APPIAN_BASE_URL}{endpoint}"
    if files:
        r = SESSION.post(url, files=files, timeout=60, **kwargs)
    else:
        r = SESSION.post(url, json=json_body, timeout=30, **kwargs)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"status": r.status_code, "text": r.text}


def _patch(endpoint: str, json_body: dict) -> dict:
    url = f"{APPIAN_BASE_URL}{endpoint}"
    r = SESSION.patch(url, json=json_body, timeout=30)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"status": r.status_code, "text": r.text}


def _delete(endpoint: str) -> dict:
    url = f"{APPIAN_BASE_URL}{endpoint}"
    r = SESSION.delete(url, timeout=30)
    r.raise_for_status()
    return {"status": r.status_code, "deleted": True}


def _build_appian_zip(interface_name: str, sail_code: str) -> bytes:
    """
    Builds an in-memory Appian-importable ZIP for a single Interface object.
    Update _manifest.json / interface JSON structure once Appian confirms format.
    """
    object_uuid = str(uuid.uuid4())

    manifest = {
        "appianPackageExportFormatVersion": "1",
        "objects": [
            {
                "type": "Interface",
                "name": interface_name,
                "uuid": object_uuid,
            }
        ],
    }

    interface_obj = {
        "entity": {
            "id":   object_uuid,
            "name": interface_name,
            "type": "Interface",
            "uuid": object_uuid,
        },
        "contents": {
            "sailCode": sail_code,
        },
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("_manifest.json", json.dumps(manifest, indent=2))
        zf.writestr(
            f"interface/{interface_name}.json",
            json.dumps(interface_obj, indent=2),
        )
    return buf.getvalue()


# ══════════════════════════════════════════════════════
# TOOL 1 — Deploy SAIL interface
# ══════════════════════════════════════════════════════

@mcp.tool()
def deploy_sail_interface(interface_name: str, sail_code: str) -> str:
    """
    Package SAIL code and deploy it to Appian as an Interface object.

    Args:
        interface_name : Name of the Appian interface (no spaces, PascalCase).
        sail_code      : Complete SAIL expression starting with a!localVariables(
                         or a top-level layout component.

    Returns:
        JSON with deployment UUID and initial status.

    Example natural-language request:
        "Deploy an intake form called EmployeeOnboardingForm with this SAIL: ..."
    """
    zip_bytes = _build_appian_zip(interface_name, sail_code)

    zip_filename = f"{interface_name}.zip"
    files = {
        "file": (zip_filename, zip_bytes, "application/zip"),
    }

    try:
        # Appian Deployment REST API — adjust path for your Appian version
        result = _post("/api/deployment", files=files)
        return json.dumps({"success": True, "deployment": result}, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({
            "success": False,
            "http_status": exc.response.status_code,
            "detail": exc.response.text,
            "hint": (
                "If you see APNX-1-4154-000 the package format needs updating. "
                "Export a test interface from Appian Designer and share the ZIP "
                "so the skill can be updated with the exact format."
            ),
        }, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 2 — Check deployment status
# ══════════════════════════════════════════════════════

@mcp.tool()
def get_deployment_status(deployment_uuid: str) -> str:
    """
    Check the status of an Appian deployment.

    Args:
        deployment_uuid : UUID returned by deploy_sail_interface.

    Returns:
        JSON with current deployment status (PENDING, IN_PROGRESS, SUCCESS, FAILED).

    Example natural-language request:
        "Check the status of deployment abc-123"
    """
    try:
        result = _get(f"/api/deployment/{deployment_uuid}")
        return json.dumps(result, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 3 — Query records
# ══════════════════════════════════════════════════════

@mcp.tool()
def query_records(
    record_type_id: str,
    filters: str = None,
    fields: str = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """
    Query records from an Appian Record Type.

    Args:
        record_type_id : Appian record type identifier (e.g. "Employee").
        filters        : Optional JSON array of filter objects.
                         Example: '[{"field":"status","operator":"=","value":"Active"}]'
        fields         : Optional comma-separated list of fields to return.
                         Example: "id,name,department,hireDate"
        limit          : Max records to return (default 50, max 1000).
        offset         : Pagination offset (default 0).

    Returns:
        JSON array of matching records.

    Example natural-language requests:
        "Show me all active employees from Appian"
        "Get the first 10 orders with status Shipped"
    """
    body = {"pagingInfo": {"startIndex": offset + 1, "batchSize": limit}}

    if filters:
        try:
            body["filters"] = json.loads(filters)
        except json.JSONDecodeError:
            return json.dumps({"error": "filters must be valid JSON array"})

    if fields:
        body["fields"] = [f.strip() for f in fields.split(",")]

    try:
        result = _post(f"/api/records/type/{record_type_id}/records", body)
        return json.dumps(result, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 4 — Create record
# ══════════════════════════════════════════════════════

@mcp.tool()
def create_record(record_type_id: str, record_data: str) -> str:
    """
    Create a new record in an Appian Record Type.

    Args:
        record_type_id : Appian record type identifier.
        record_data    : JSON object of field name → value pairs.
                         Example: '{"name":"Alice Wong","department":"Engineering","status":"Active"}'

    Returns:
        JSON with the created record's ID and fields.

    Example natural-language request:
        "Create a new employee record for Alice Wong in Engineering"
    """
    try:
        data = json.loads(record_data)
    except json.JSONDecodeError:
        return json.dumps({"error": "record_data must be valid JSON object"})

    try:
        result = _post(f"/api/records/type/{record_type_id}/record", data)
        return json.dumps(result, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 5 — Update record
# ══════════════════════════════════════════════════════

@mcp.tool()
def update_record(record_type_id: str, record_id: str, updates: str) -> str:
    """
    Update fields on an existing Appian record.

    Args:
        record_type_id : Appian record type identifier.
        record_id      : ID of the record to update.
        updates        : JSON object of field name → new value pairs.
                         Example: '{"status":"Inactive","exitDate":"2026-05-06"}'

    Returns:
        JSON with the updated record.

    Example natural-language request:
        "Update employee record 1042 — set status to Inactive"
    """
    try:
        data = json.loads(updates)
    except json.JSONDecodeError:
        return json.dumps({"error": "updates must be valid JSON object"})

    try:
        result = _patch(f"/api/records/type/{record_type_id}/record/{record_id}", data)
        return json.dumps(result, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 6 — Delete record
# ══════════════════════════════════════════════════════

@mcp.tool()
def delete_record(record_type_id: str, record_id: str) -> str:
    """
    Delete a record from an Appian Record Type.

    Args:
        record_type_id : Appian record type identifier.
        record_id      : ID of the record to delete.

    Returns:
        JSON confirming deletion.

    Example natural-language request:
        "Delete employee record 1042 from Appian"
    """
    try:
        result = _delete(f"/api/records/type/{record_type_id}/record/{record_id}")
        return json.dumps(result, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 7 — Call custom Web API
# ══════════════════════════════════════════════════════

@mcp.tool()
def call_web_api(
    api_path: str,
    http_method: str = "GET",
    request_body: str = None,
    query_params: str = None,
) -> str:
    """
    Call any custom Web API defined in your Appian application.

    Args:
        api_path      : Path to the Web API as configured in Appian Designer.
                        Example: "/orders/summary" or "/employees/search"
        http_method   : GET | POST | PUT | PATCH | DELETE  (default: GET)
        request_body  : Optional JSON string for the request body.
        query_params  : Optional JSON object of query string parameters.
                        Example: '{"status":"Active","department":"Engineering"}'

    Returns:
        JSON response from the Web API.

    Example natural-language requests:
        "Call the Appian orders summary API"
        "POST to /employees/promote with body {employeeId: 42, newTitle: 'Manager'}"
    """
    url = f"{APPIAN_BASE_URL}/api/webapi{api_path}"

    params = None
    if query_params:
        try:
            params = json.loads(query_params)
        except json.JSONDecodeError:
            return json.dumps({"error": "query_params must be valid JSON object"})

    body = None
    if request_body:
        try:
            body = json.loads(request_body)
        except json.JSONDecodeError:
            return json.dumps({"error": "request_body must be valid JSON"})

    try:
        r = SESSION.request(
            method=http_method.upper(),
            url=url,
            json=body,
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        try:
            return json.dumps(r.json(), indent=2)
        except Exception:
            return r.text
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 8 — Start process
# ══════════════════════════════════════════════════════

@mcp.tool()
def start_process(process_model_id: str, inputs: str = None) -> str:
    """
    Start an Appian process model instance.

    Args:
        process_model_id : The numeric ID or UUID of the Appian process model.
        inputs           : Optional JSON object of process input variable values.
                           Example: '{"employeeId":42,"department":"Sales"}'

    Returns:
        JSON with the new process instance ID and status.

    Example natural-language request:
        "Start the employee onboarding process for employee ID 42"
    """
    body = {"processModelId": process_model_id}

    if inputs:
        try:
            body["inputs"] = json.loads(inputs)
        except json.JSONDecodeError:
            return json.dumps({"error": "inputs must be valid JSON object"})

    try:
        result = _post("/api/processes", body)
        return json.dumps(result, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ══════════════════════════════════════════════════════
# TOOL 9 — Get process status
# ══════════════════════════════════════════════════════

@mcp.tool()
def get_process_status(process_instance_id: str) -> str:
    """
    Get the current status and details of an Appian process instance.

    Args:
        process_instance_id : ID of the process instance returned by start_process.

    Returns:
        JSON with process status, active tasks, and variable values.

    Example natural-language request:
        "What's the status of process instance 8765?"
    """
    try:
        result = _get(f"/api/processes/{process_instance_id}")
        return json.dumps(result, indent=2)
    except requests.HTTPError as exc:
        return json.dumps({"error": exc.response.text}, indent=2)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Starting Appian MCP Server → {APPIAN_BASE_URL}")
    mcp.run(transport="stdio")
