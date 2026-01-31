# Implementation Plan: Agent Communication Server

## 1. Technical Context

- **Framework**: `FastAPI`
- **Port**: `8000`
- **Protocol**: HTTP + SSE (Server-Sent Events)
- **Architecture**: Monolithic, Stateless
- **Dependencies**: `ag-core`, `ag-ui` (implied constructs), `uvicorn`

## 2. Constitution Check

- **Agent-First**: Yes, the server is the primary interface for agents.
- **Atomic Evolution**: New branch, isolated feature.
- **Separation of Concerns**: Backend logic isolated from Frontend (served via API).

## 3. Phase 1: Design & Contracts

### 3.1 Data Model

See `data-model.md`.

- **Request**: `ChatRequest`
- **Events**: `Chunk`, `Tool`, `Error`

### 3.2 API Contract

See `contracts/openapi.yaml` (mock).

- `POST /api/chat/{agent_id}` -> Streams events.

### 3.3 Quickstart

See `quickstart.md`.

- Instructions to install deps and run server.

## 4. Phase 2: Implementation Steps

1. **Scaffold Server**: Create `main.py` with FastAPI app and CORS.
2. **Implement Agent Registry**: Mechanism to load/import agents.
3. **Create Endpoint**: `POST /api/chat` with `StreamingResponse`.
4. **Integrate Agents**: Connect `agent_id` parameter to actual Agent execution.
5. **Verify**: Test with curl/script.

## 5. Gates

- [x] Research complete
- [x] Constitution aligned
- [ ] Design artifacts created (Next Step)
