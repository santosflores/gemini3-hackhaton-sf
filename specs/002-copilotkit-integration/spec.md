# Specification: CopilotKit Integration with AG-UI Protocol

## 1. Background & Context

The project aims to enhance the user interface by integrating **CopilotKit**, enabling a rich, AI-powered chat experience. The backend, a FastAPI server hosting agents, needs to communicate with this new UI. The chosen communication protocol is **ag-ui**. The integration requires a POST endpoint on the backend that handles session negotiation and streams events back to the client in the required format.

## 2. User Scenarios

- **Scenario 1: User Initiates Chat**
  - **Actor**: End User
  - **Action**: Opens the application and types a message into the CopilotKit chat interface.
  - **Outcome**: The message is sent to the backend. The backend establishes/verifies a session and streams the agent's response back. The UI updates in real-time as events are received.

- **Scenario 2: Agent Tool Usage**
  - **Actor**: Backend Agent
  - **Action**: Decides to use a tool during processing.
  - **Outcome**: The agent execution stream includes tool usage events formatted in `ag-ui`. The CopilotKit UI renders these events (e.g., showing "Searching...", showing intermediate results) appropriate to the user.

## 3. Functional Requirements

- **FR1: FastAPI Endpoint**
  - The system MUST expose a specific `POST` endpoint (e.g., `/copilotkit` or `/agent/stream`).
  - This endpoint MUST accept chat messages and context from the CopilotKit client.
  - The endpoint MUST return a streaming response (Server-Sent Events or compatible stream).

- **FR2: AG-UI Protocol Implementation**
  - The streaming response MUST adhere to the `ag-ui` protocol standards.
  - Events for text chunks, tool calls, and errors MUST be formatted correctly so the frontend can parse them.

- **FR3: Session Management**
  - The endpoint MUST handle session negotiation/validation as part of the request lifecycle.
  - State (if any) should be managed or referenced via a session ID.

- **FR4: Frontend Integration**
  - The Frontend Application MUST be updated to include CopilotKit components.
  - The CopilotKit provider/hook MUST be configured to point to the new backend endpoint.
  - **Clarification**: Parameter `ag-ui` translation strategy is **Adapter Layer**. We will build a frontend/backend adapter to translate `ag-ui` events into CopilotKit's format, keeping protocols decoupled.

- **FR5: Agent Adaptation**
  - The existing agents MUST be compatible with the streaming response format.
  - **Clarification**: Agents natively output `ag-ui` events. The integration works directly with these streams.

## 4. Success Criteria

- **SC1**: A user can send a message from the CopilotKit UI and receive a streaming text response.
- **SC2**: Tool usage by the agent is visible in the UI (not just the final answer).
- **SC3**: The application handles multiple concurrent sessions correctly.
- **SC4**: Network disconnection or backend errors are gracefully handled in the UI.

## 5. Key Entities

- **CopilotKit UI**: The frontend component library.
- **AG-UI Protocol**: The schema/format for messages and events.
- **Agent Endpoint**: The FastAPI operational point for the UI.

## 6. Assumptions

- The `copilotkit` libraries are installed or can be installed in the frontend project.
- The `ag-ui` protocol definition is available in the codebase or documentation.
- The existing agent system (Google ADK agents) is functional and can be invoked programmatically.

## 7. Clarifications

### Session 2026-01-31

- Q: How should we bridge CopilotKit and AG-UI? → A: **Adapter Layer**. Custom adapter to translate events.
- Q: How is the session negotiated? → A: **Implicit/Payload**. Session ID sent in request body/headers; auto-created if missing.
- Q: Do agents output AG-UI events? → A: **Yes, Native**. No wrapper needed for the core agent output.
