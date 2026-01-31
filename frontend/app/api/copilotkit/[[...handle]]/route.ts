/**
 * CopilotKit API Route - Proxies requests to the backend AG-UI agent
 *
 * Uses HttpAgent from @ag-ui/client to connect to the backend.
 */
import {
    CopilotRuntime,
    createCopilotEndpoint,
} from "@copilotkitnext/runtime";
import { HttpAgent } from "@ag-ui/client";
import { handle } from "hono/vercel";
import { config } from "dotenv";

config();

// Use HttpAgent for AG-UI protocol compatibility
const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
console.log("CopilotKit API Route initializing with BACKEND_URL:", backendUrl);

const runtime = new CopilotRuntime({
    agents: {
        default: new HttpAgent({
            agentId: "default",
            url: `${backendUrl}/agent-default`,
            description: "Orchestrator Agent", // Description is required by AbstractAgent/AgentConfig
        }),
    },
});

const app = createCopilotEndpoint({
    runtime,
    basePath: "/api/copilotkit",
});

const handler = handle(app);

export const POST = handler;
export const GET = handler;
export const OPTIONS = handler;
