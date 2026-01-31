# Data Model

## Entities

### ChatRequest

Represents a user's input to an agent.

- `input` (string, required): The user's message or prompt.
- `agent_id` (string, required): The identifier of the target agent (e.g., "orchestrator", "intake").
- `context` (object, optional): Arbitrary JSON dictionary for client-managed history or state.

### SSE Events

The stream consists of the following event types:

#### `text`

- `data`: (string) Partial logic or thought text.

#### `message`

- `data`: (JSON) Function/Tool call payload.

#### `result`

- `data`: (string) Final answer/response text.

#### `error`

- `data`: (JSON) Error details `{ "code": 500, "message": "..." }`.
