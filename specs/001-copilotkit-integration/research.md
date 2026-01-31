# Research: CopilotKit & AG-UI Integration

## 1. Interaction Protocol

**Decision**: Use `copilotkit` Python SDK to handle the protocol automatically.

**Rationale**:

- The user pointed out `add_fastapi_endpoint`, which is part of `copilotkit.integrations.fastapi`.
- This function wraps a CopilotKit-compatible agent and exposes it via FastAPI, handling strict AG-UI protocol details (SSE, event types) automatically.
- This significantly reduces the risk of protocol mismatch and implementation effort.

## 2. Google ADK Integration

**Decision**: Implement a `CopilotKitAgent` adapter for `google.adk.Agent`.

**Rationale**:

- CopilotKit likely requires agents to adhere to its own `Agent` interface (or generic callable).
- We will create a class `ADKCopilotAgent` that:
  1. Accepts user messages from CopilotKit.
  2. Converts them to ADK input format.
  3. Invokes the ADK agent (streaming mode).
  4. Yields ADK events (text chunks, tool calls) mapped to CopilotKit events.

## 3. Session Management

**Decision**: Stateless (per Plan), leveraging CopilotKit's context passing.

**Rationale**:

- The `add_fastapi_endpoint` likely handles basic request parsing.
- We will rely on the `messages` list passed in each request to re-hydrate the ADK agent's state if necessary, or pass it directly if ADK is stateless/supports full history input.

## 4. Implementation Technology

**Backend**:

- `copilotkit` (Python SDK).
- `google.adk` (Existing).
- `FastAPI` (Existing).
