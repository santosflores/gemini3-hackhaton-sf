# Data Model: CopilotKit Adapter

## Internal Entities

### `ADKToCopilotMap`

Since we are using the SDK, the data model focus shifts to the _mapping_ logic in the adapter.

| ADK Concept  | CopilotKit Concept | Notes                        |
| ------------ | ------------------ | ---------------------------- |
| `text_chunk` | `TextMessage`      | Streamed content             |
| `ToolCall`   | `ActionExecution`  | Represents a tool call start |
| `ToolResult` | `ActionResult`     | Represents tool completion   |

## API Model (Managed by SDK)

The `copilotkit` SDK manages the external API model.

- **Endpoint**: `/copilotkit` (or similar)
- **Method**: `POST`
- **Body**: standard CopilotKit payload.
