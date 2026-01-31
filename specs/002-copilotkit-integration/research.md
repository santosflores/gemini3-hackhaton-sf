# Research Notes: CopilotKit Integration

## Executive Summary

Research confirms that CopilotKit is built around the **AG-UI (Agent-User Interaction)** protocol. This significantly simplifies the integration as the backend (using `ag-ui-adk`) and the frontend (using `@copilotkit/react-core`) share a common language. The "Adapter Layer" initially thought necessary will likely be minimal configuration rather than a complex translation layer.

## Key Findings

### 1. Protocol Compatibility

- **Decision**: Use native CopilotKit streaming with `ag-ui` payload.
- **Rationale**: CopilotKit _implements_ AG-UI. It is an event-based protocol for agent-user interaction.
- **Verification**: Search results indicate AG-UI is the core protocol for CopilotKit. The backend's `ag-ui-adk` library is the Python implementation counterpart to the React frontend libraries.

### 2. Frontend Integration

- **Decision**: Use `@copilotkit/react-core` and `@copilotkit/react-ui`.
- **Target Hook**: `useCopilotChat` (or `useCopilotChatHeadless_c` for advanced control if needed).
- **Configuration**: The `CopilotKit` provider needs to point to our FastAPI endpoint.

### 3. Session Negotiation

- **Decision**: Implicit session handling via the POST request payload.
- **Rationale**: CopilotKit sends context and message history in its requests. The backend `ag-ui-adk` should handle unmarshalling this session state.

## Implementation Implications

- **Backend**: Focus on exposing the endpoint using `ag-ui-adk` utilities. Ensure the `stream` response content type is correct (usually `text/event-stream` or `application/x-ndjson` depending on the exact transport CopilotKit expects - likely SSE).
- **Frontend**: Standard CopilotKit setup. Point the `url` to our new endpoint.

## Resolved Unknowns

| Unknown                 | Resolution                                                      |
| ----------------------- | --------------------------------------------------------------- |
| CopilotKit/AG-UI Bridge | **Native Compatibility**. They are the same protocol ecosystem. |
| React Hook Version      | Use `useCopilotChat` from latest `@copilotkit/react-core`.      |
| Session Negotiation     | Handled within the AG-UI protocol payload.                      |
