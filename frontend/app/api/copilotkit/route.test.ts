import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NextRequest } from 'next/server';

// Use vi.hoisted to ensure the mock is available during module loading
const { mockHandleRequest } = vi.hoisted(() => ({
    mockHandleRequest: vi.fn().mockResolvedValue(new Response('OK'))
}));

// Mock CopilotKit modules before importing the route
vi.mock('@copilotkit/runtime', () => {
    class MockCopilotRuntime {
        constructor(_config: unknown) { }
    }
    class MockEmptyAdapter { }
    return {
        CopilotRuntime: MockCopilotRuntime,
        ExperimentalEmptyAdapter: MockEmptyAdapter,
        copilotRuntimeNextJSAppRouterEndpoint: vi.fn().mockReturnValue({
            handleRequest: mockHandleRequest
        })
    };
});

vi.mock('@copilotkit/runtime/langgraph', () => {
    class MockLangGraphHttpAgent {
        url: string;
        constructor(config: { url: string }) {
            this.url = config.url;
        }
    }
    return {
        LangGraphHttpAgent: MockLangGraphHttpAgent
    };
});

vi.mock('dotenv', () => ({
    config: vi.fn()
}));

// Import after mocking
import { POST } from './[[...handle]]/route';
import { copilotRuntimeNextJSAppRouterEndpoint } from '@copilotkit/runtime';

const DISCOVERY_URL = 'http://localhost/api/copilotkit';

describe('CopilotKit API Route', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('POST handler', () => {
        it('calls copilotRuntimeNextJSAppRouterEndpoint with correct config', async () => {
            const mockRequest = new NextRequest(DISCOVERY_URL, {
                method: 'POST',
                body: JSON.stringify({ message: 'test' })
            });

            await POST(mockRequest);

            expect(copilotRuntimeNextJSAppRouterEndpoint).toHaveBeenCalledWith({
                runtime: expect.any(Object),
                serviceAdapter: expect.any(Object),
                endpoint: '/api/copilotkit'
            });
        });

        it('invokes handleRequest with the incoming request', async () => {
            const mockRequest = new NextRequest(DISCOVERY_URL, {
                method: 'POST',
                body: JSON.stringify({ message: 'hello' })
            });

            await POST(mockRequest);

            expect(mockHandleRequest).toHaveBeenCalledWith(mockRequest);
        });

        it('returns the response from handleRequest', async () => {
            const mockResponse = new Response('Custom Response');
            mockHandleRequest.mockResolvedValueOnce(mockResponse);

            const mockRequest = new NextRequest(DISCOVERY_URL, {
                method: 'POST'
            });

            const result = await POST(mockRequest);

            expect(result).toBe(mockResponse);
        });
    });
});
