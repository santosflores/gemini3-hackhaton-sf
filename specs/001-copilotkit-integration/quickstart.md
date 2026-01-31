# Quickstart: CopilotKit Integration (SDK)

## Prerequisites

- Backend: `pip install copilotkit`
- Active Google ADK environment.

## Backend Integration

1. **Import**:

   ```python
   from fastapi import FastAPI
   from copilotkit.integrations.fastapi import add_fastapi_endpoint
   from copilotkit import CopilotKitRemoteEndpoint
   ```

2. **Setup**:

   ```python
   app = FastAPI()
   sdk = CopilotKitRemoteEndpoint(agents=[my_adk_agent_adapter])
   add_fastapi_endpoint(app, sdk, "/copilotkit")
   ```

3. **Verify**:
   Use `curl` or the CopilotKit `CopilotSidebar` pointing to `/copilotkit`.

## Frontend Setup

1. **Provider**:
   ```jsx
   <CopilotKit url="http://localhost:8000/copilotkit" ... />
   ```
