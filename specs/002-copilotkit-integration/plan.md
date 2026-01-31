# Implementation Plan - CopilotKit Integration

## Technical Context

**Feature**: [Link to spec.md](./spec.md)

### Architecture Overview

This feature integrates CopilotKit into the frontend to provide a conversational AI interface. The backend will expose a streaming endpoint (`/copilotkit/stream` likely) that adheres to the established `ag-ui` protocol. We will implement an Adapter Layer on the frontend (or adjacent helper) to translate between CopilotKit's internal event format and `ag-ui` events. The backend agents already output compatible events, so the backend focus is on the streaming mechanics and session handling.

### Technology Choices

| Area                    | Choice                   | Rationale                                                    |
| ----------------------- | ------------------------ | ------------------------------------------------------------ |
| **Frontend Lib**        | `CopilotKit`             | Requested by user for UI components and state management.    |
| **Protocol**            | `ag-ui`                  | Existing project standard for agent communication.           |
| **Integration Pattern** | Adapter Pattern          | Decouples the specific UI library from the backend protocol. |
| **Transport**           | Server-Sent Events (SSE) | Standard for streaming text/events; widely supported.        |

### Unknowns & Risks

- [NEEDS CLARIFICATION] Specific CopilotKit React hooks/components version and compatibility with our current React setup.
- [NEEDS CLARIFICATION] exact structure of existing `ag-ui` events (need to inspect code).

## Constitution Check

**Constitution**: [Link to constitution.md](../../.specify/memory/constitution.md)

| Principle                        | Compliance | Notes                                                                                 |
| -------------------------------- | ---------- | ------------------------------------------------------------------------------------- |
| **Agent-First Architecture**     | Yes        | Using `ag-ui` ensures agents drive the interaction. Streaming improves "chat" feel.   |
| **Atomic Evolution**             | Yes        | Feature is isolated to a new integration module/endpoint.                             |
| **Clear Separation of Concerns** | Yes        | Backend logic remains agnostic of UI library thanks to the protocol/adapter approach. |

## Phase 0: Outline & Research

[Link to research.md](./research.md)

## Phase 1: Design & Contracts

- [ ] Data Model: [Link to data-model.md](./data-model.md)
- [ ] API Contracts: [Link to contracts/](./contracts/)
- [ ] Quickstart: [Link to quickstart.md](./quickstart.md)

## Phase 2: Implementation Steps

(Start with Phase 1 completion)
