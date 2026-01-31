<!-- SYNC IMPACT REPORT
Version change: (New) -> 1.0.0
- List of modified principles: Initial Creation
- Added sections: Governance, Principles, Mission
- Templates requiring updates: N/A
- Follow-up TODOs: None
-->

# Project Constitution: Gemini 3 Hackathon SF

> **Ratified:** 2026-01-31
> **Last Amended:** 2026-01-31
> **Version:** 1.0.0

## 1. Mission & Values

The mission of Gemini 3 Hackathon SF is to build a robust, agent-native backend and frontend system that leverages the Google ADK framework to enable powerful AI agent interactions. The end goal is to help sports coaches to predict the next play, allow the coach to have a two communication channel with the AI agent to discuss the suggestion via text or voice.

### Principle 1: Agent-First Architecture

The system MUST be designed with AI agents as first-class users. APIs should be self-documenting, deterministic where possible, and robust against variable inputs. Context windows are finite resources; data density and relevance are prioritized over verbosity.

### Principle 2: Atomic Evolution

Changes to the codebase MUST be atomic, self-contained, and verifiable. We commit frequently with clear, descriptive messages. This facilitates easier debugging, rollback, and agent-assisted coding.

### Principle 3: Clear Separation of Concerns

The architecture MUST maintain a strict boundary between the Frontend (Presentation) and Backend (Logic/Data). The backend serves as the source of truth, exposing well-defined endpoints for the frontend and AI agents.

## 2. Governance

### Amendment Process

This constitution may be amended by a Pull Request that explicitly references the "speckit.constitution" workflow. Amendments require a version bump.

### Versioning Policy

This project adheres to Semantic Versioning (MAJOR.MINOR.PATCH) for its governance documents.

- **MAJOR**: Fundamental changes to principles or mission.
- **MINOR**: Addition of new principles or significant expansions.
- **PATCH**: Clarifications, formatting, or minor adjustments.

### Compliance

All architectural decisions and code changes SHOULD be weighed against these principles. Use the `/speckit.analyze` workflow to audit major features against this constitution.
