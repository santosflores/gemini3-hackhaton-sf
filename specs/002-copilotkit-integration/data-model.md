# Data Model: CopilotKit Integration

## Overview

The integration relies primarily on the **AG-UI Protocol** message definitions. The backend does not need to persist chat history in a database for this stateless implementation (history is client-managed/sent by CopilotKit), but we define the transient entities here.

## Entities

### 1. ChatMessage (Transient)

Represents a single exchange in the conversation.

- **Source**: User (Frontend) or Agent (Backend)
- **Format**: JSON / AG-UI Event
- **Fields**:
  - `id`: string (UUID)
  - `role`: string ("user", "assistant", "system")
  - `content`: string (text content)
  - `tool_calls`: array (optional, for agent tool use)

### 2. CopilotRequest

The payload sent by the CopilotKit frontend to the backend.

- **Fields**:
  - `messages`: List<ChatMessage> (Conversation history)
  - `context`: Object (Frontend application state/context)
  - `session_id`: string (Optional, for continuity)

### 3. CopilotResponseEvent (Streamed)

The individual events streamed back to the client.

- **Type**: Server-Sent Event (SSE)
- **Structure**: AG-UI Event schema
- **Types**:
  - `text`: Incremental text updates.
  - `tool_start`: Indicator that a tool is being called.
  - `tool_result`: Output of a tool call.
  - `tool_end`: completion of tool interaction.

## State Management

- **Session State**: Managed by the Client (CopilotKit). The full relevant history is sent with each request.
- **Agent State**: Short-lived, exists only during the processing of a single request stream.
