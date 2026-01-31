# Research: Agent Communication Server

## 1. Fast API Server-Sent Events (SSE)

**Decision**: Use `ssevents` or standard `StreamingResponse` from FastAPI.
**Rationale**: `StreamingResponse` with a generator is the native FastAPI way to handle SSE. It keeps dependencies low.
**Alternatives**: `fastapi-sse` (external lib), WebSockets (rejected per spec Clarification for SSE).

## 2. Polymorphic Endpoint Routing

**Decision**: Use a dictionary registry or dynamic import pattern based on `agent_id`.
**Rationale**: Allows adding new agents without modifying the router code significantly.
**Pattern**: `agents = {"intake": IntakeAgent, "orchestrator": OrchestratorAgent}`.

## 3. CORS Configuration

**Decision**: Use `fastapi.middleware.cors.CORSMiddleware`.
**Rationale**: Standard, robust, and supports the specific origin requirement (`localhost:3000`).

## 4. Pending Questions

- None. Clarification phase resolved architecture and protocol questions.
