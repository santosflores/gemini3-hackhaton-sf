# Specification: Agent Communication Server

## 1. Background & Context

The project requires a FastAPI backend server to serve as the orchestration layer for agent and subagent communications. This server will utilize `ag-core` for rapid endpoint development and adhere to the `ag-ui` protocol for communication. It needs to support cross-origin requests, specifically from a frontend running on port 3000.

## 2. User Scenarios

- **Scenario 1: Agent Triggering**
  - **Actor**: User (via Frontend or API Client)
  - **Action**: Sends a request to trigger an agent action.
  - **Outcome**: The server receives the request, orchestrates the communication with the appropriate agent/subagent, and returns the response.

- **Scenario 2: Frontend Integration**
  - **Actor**: Frontend Application (localhost:3000)
  - **Action**: Makes an HTTP request to the backend.
  - **Outcome**: The request is accepted (CORS allowed) and processed.

## 3. Functional Requirements

- **FR1: Server Infrastructure**
  - The backend MUST be built using `FastAPI`.
  - The server MUST listen on port `8000` by default.
  - The server MUST utilize `ag-core` to facilitate endpoint creation.
  - **Clarification**: The server architecture MUST be **Stateless**. Request context and history are managed by the client.

- **FR2: Communication Protocol**
  - The server MUST implement endpoints compatible with the `ag-ui` protocol.
  - The server MUST be able to trigger communication with the main agent and specialized subagents.
  - **Clarification**: Endpoints MUST support **Server-Sent Events (SSE)** to stream agent thoughts, tool calls, and final responses in real-time.
  - **Clarification**: The API MUST expose a **single polymorphic endpoint** (e.g., `/api/chat` or `/agent/interact`) that accepts an `agent_id` or similar routing key to dynamically accept requests for different agents.

- **FR3: Security & Access Control**
  - CORS middleware MUST be configured.
  - The CORS configuration MUST explicitly allow requests from `http://localhost:3000`.
  - Multiple clients MUST be able to access the server.
  - **Clarification**: No authentication mechanism is required/enforced for this version (Public API).

- **FR4: Orchestration**
  - The server MUST handle routing of requests to the correct agent or subagent context.
  - **Clarification**: Agents are integrated directly into the server process (Monolithic). The server MUST import and instantiate Agent classes directly rather than calling external services.

## 4. Success Criteria

- **SC1**: Server successfully starts on port 8000 without errors.
- **SC2**: A `curl` request from a different origin (mocking localhost:3000) is accepted (CORS headers present).
- **SC3**: An endpoint exists that fulfills the `ag-ui` protocol requirements.
- **SC4**: Integration with `ag-core` is verified (e.g., server uses `ag-core` components).

## 5. Key Entities

- **Agent**: The primary AI entity.
- **Subagent**: Specialized AI entities managed by the main agent.
- **Message**: The unit of communication formatted according to `ag-ui` protocol.

## 6. Assumptions

- `ag-ui` and `ag-core` are available in the project's dependency list or Python environment.
- The "agent" and "subagents" code structure exists or will be scaffolded within the backend.

## 7. Clarifications

### Session 2026-01-31

- Q: How should the server communicate with the agents (architecture)? → A: **Direct Import & Execution** (Monolithic). The server allows direct interaction with the python objects.
- Q: What interaction mode should be used? → A: **Streaming (SSE)**. The server will stream partial results and thoughts to the client.
- Q: How should API endpoints be structured? → A: **Single Polymorphic Endpoint**. One endpoint routes to specific agents via parameters.
- Q: How is conversation state managed? → A: **Stateless (Client-Managed)**. The server does not persist history; client sends context.
- Q: What authentication is needed? → A: **No Authentication (Public)**. API is open; security relies on network/CORS only.
