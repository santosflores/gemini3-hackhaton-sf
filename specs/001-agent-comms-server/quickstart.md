# Quickstart: backend

## Prerequisites

- Python 3.10+
- `pip`

## Installation

1. Navigate to `backend/`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

1. Run uvicorn:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Testing

1. Use curl to test connectivity:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"agent_id": "orchestrator", "input": "Hello"}'
   ```
