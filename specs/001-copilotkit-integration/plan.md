# Implementation Plan - CopilotKit Integration

## Technical Context

**Feature**: [Link to spec.md](./spec.md)

### Architecture Overview

We will leverage the `copilotkit` Python SDK to expose our Google ADK agent.

- A new adapter class `ADKCopilotAgent` will bridge the gap between `google.adk.Agent` and CopilotKit's expectations.
- We will use `add_fastapi_endpoint` in `main.py` to register this agent at `/copilotkit`.
- The frontend will utilize `useCopilotChat` pointing to this endpoint.

### Technology Choices

| Area        | Choice                  | Rationale                                    |
| ----------- | ----------------------- | -------------------------------------------- |
| Frontend    | CopilotKit (React)      | User request.                                |
| Backend SDK | `copilotkit` Python SDK | Simplifies AG-UI protocol compliance.        |
| Core Agent  | Google ADK              | Existing agent logic.                        |
| Integration | `add_fastapi_endpoint`  | Recommended utility for FastAPI integration. |

### Unknowns & Risks

- [NEEDS CLARIFICATION] Specific import path for `add_fastapi_endpoint` (likely `copilotkit.integrations.fastapi`).
- [NEEDS CLARIFICATION] The exact abstract method signatures required by CopilotKit's `Agent` class (if creating a custom one).

## Constitution Check

**Constitution**: [Link to constitution.md](../../.specify/memory/constitution.md)

| Principle              | Compliance | Notes                                                                   |
| ---------------------- | ---------- | ----------------------------------------------------------------------- |
| Agent-First            | Yes        | Using specialized SDKs to expose agents.                                |
| Atomic Evolution       | Yes        | Integration is self-contained in adapter and main config.               |
| Separation of Concerns | Yes        | Adapter handles translation; Agent handles logic; SDK handles protocol. |

## Phase 0: Outline & Research

[Link to research.md](./research.md)

## Phase 1: Design & Contracts

- [ ] Data Model: [Link to data-model.md](./data-model.md)
- [ ] API Contracts: (Implicit via SDK, but verified) [Link to contracts/](./contracts/)
- [ ] Quickstart: [Link to quickstart.md](./quickstart.md)

## Phase 2: Implementation Steps

(Start with Phase 1 completion)
