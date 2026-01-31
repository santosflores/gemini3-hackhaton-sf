# Quickstart: CopilotKit Integration

## Prerequisites

- Backend running (`fastapi dev app/main.py`)
- Frontend application (Next.js/React) set up

## Backend Setup

1. Verify `ag-ui-adk` is installed.
2. Ensure the `/copilotkit/stream` endpoint is mounted in `app/main.py` (or similar router).

## Frontend Setup

1. Install CopilotKit:

   ```bash
   npm install @copilotkit/react-core @copilotkit/react-ui
   ```

2. Wrap your application in `<CopilotKit>`:

   ```jsx
   import { CopilotKit } from "@copilotkit/react-core";
   import "@copilotkit/react-ui/styles.css";

   export default function App({ Component, pageProps }) {
     return (
       <CopilotKit url="http://localhost:8000/copilotkit/stream">
         <Component {...pageProps} />
       </CopilotKit>
     );
   }
   ```

3. Use the Sidebar or Chat components:

   ```jsx
   import { CopilotSidebar } from "@copilotkit/react-ui";

   return (
     <>
       <YourAppContent />
       <CopilotSidebar />
     </>
   );
   ```

## Testing

1. Start Backend: `http://localhost:8000`
2. Start Frontend: `http://localhost:3000`
3. Open Frontend, type "Hello" in the Copilot Sidebar.
4. Verify the agent responds.
