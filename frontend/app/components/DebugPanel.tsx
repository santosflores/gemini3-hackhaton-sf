"use client";

import { useState, useEffect, useCallback, useRef } from "react";

// Event types from AG-UI protocol
type EventType =
    | "RUN_STARTED"
    | "RUN_FINISHED"
    | "RUN_ERROR"
    | "STEP_STARTED"
    | "STEP_FINISHED"
    | "TEXT_MESSAGE_START"
    | "TEXT_MESSAGE_CONTENT"
    | "TEXT_MESSAGE_END"
    | "TOOL_CALL_START"
    | "TOOL_CALL_ARGS"
    | "TOOL_CALL_END"
    | "TOOL_CALL_RESULT"
    | "STATE_SNAPSHOT"
    | "STATE_DELTA"
    | "MESSAGES_SNAPSHOT"
    | "ACTIVITY_SNAPSHOT"
    | "ACTIVITY_DELTA"
    | "RAW"
    | "CUSTOM";

interface DebugEvent {
    id: string;
    timestamp: Date;
    type: EventType | string;
    data: unknown;
}

// Color mapping for event types
const eventColorMap: Record<string, string> = {
    RUN_STARTED: "#22c55e",    // green
    RUN_FINISHED: "#22c55e",   // green
    RUN_ERROR: "#ef4444",      // red
    STEP_STARTED: "#3b82f6",   // blue
    STEP_FINISHED: "#3b82f6",  // blue
    TEXT_MESSAGE_START: "#a855f7",   // purple
    TEXT_MESSAGE_CONTENT: "#a855f7", // purple
    TEXT_MESSAGE_END: "#a855f7",     // purple
    TOOL_CALL_START: "#f59e0b",  // amber
    TOOL_CALL_ARGS: "#f59e0b",   // amber
    TOOL_CALL_END: "#f59e0b",    // amber
    TOOL_CALL_RESULT: "#f59e0b", // amber
    STATE_SNAPSHOT: "#06b6d4",   // cyan
    STATE_DELTA: "#06b6d4",      // cyan
    MESSAGES_SNAPSHOT: "#ec4899", // pink
    ACTIVITY_SNAPSHOT: "#8b5cf6", // violet
    ACTIVITY_DELTA: "#8b5cf6",    // violet
    RAW: "#6b7280",     // gray
    CUSTOM: "#14b8a6",  // teal
};

// Global event store
let globalEvents: DebugEvent[] = [];
let eventListeners: Set<() => void> = new Set();

// Intercept fetch to capture SSE events
const originalFetch = typeof window !== "undefined" ? window.fetch : null;

if (typeof window !== "undefined" && originalFetch) {
    window.fetch = async function (...args) {
        const [input, init] = args;
        const url = typeof input === "string" ? input : input instanceof URL ? input.href : (input as Request).url;

        // Only intercept copilotkit API calls
        if (url.includes("/api/copilotkit") && init?.method === "POST") {
            const response = await originalFetch.apply(this, args);

            // Clone the response to read the body
            const clonedResponse = response.clone();

            // Handle SSE streams
            if (response.headers.get("content-type")?.includes("text/event-stream")) {
                const reader = clonedResponse.body?.getReader();
                if (reader) {
                    const decoder = new TextDecoder();

                    // Process stream in background
                    (async () => {
                        try {
                            while (true) {
                                const { done, value } = await reader.read();
                                if (done) break;

                                const text = decoder.decode(value, { stream: true });
                                const lines = text.split("\n");

                                for (const line of lines) {
                                    if (line.startsWith("data:")) {
                                        try {
                                            const data = JSON.parse(line.slice(5).trim());
                                            const event: DebugEvent = {
                                                id: crypto.randomUUID(),
                                                timestamp: new Date(),
                                                type: data.type || "UNKNOWN",
                                                data,
                                            };
                                            globalEvents = [...globalEvents, event];
                                            // Notify listeners
                                            eventListeners.forEach((listener) => listener());
                                        } catch {
                                            // Not valid JSON, skip
                                        }
                                    }
                                }
                            }
                        } catch (error) {
                            console.error("Error reading stream:", error);
                        }
                    })();
                }
            }

            return response;
        }

        return originalFetch.apply(this, args);
    };
}

export function useDebugEvents() {
    const [events, setEvents] = useState<DebugEvent[]>([]);

    useEffect(() => {
        // Initial sync
        setEvents([...globalEvents]);

        // Subscribe to updates
        const listener = () => setEvents([...globalEvents]);
        eventListeners.add(listener);

        return () => {
            eventListeners.delete(listener);
        };
    }, []);

    const clearEvents = useCallback(() => {
        globalEvents = [];
        setEvents([]);
    }, []);

    return { events, clearEvents };
}

interface DebugPanelProps {
    className?: string;
}

export default function DebugPanel({ className = "" }: DebugPanelProps) {
    const { events, clearEvents } = useDebugEvents();
    const [isOpen, setIsOpen] = useState(true);
    const [isPinned, setIsPinned] = useState(false);
    const [selectedType, setSelectedType] = useState<string | null>(null);
    const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set());
    const [autoScroll, setAutoScroll] = useState(true);
    const eventListRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new events arrive
    useEffect(() => {
        if (autoScroll && eventListRef.current) {
            eventListRef.current.scrollTop = eventListRef.current.scrollHeight;
        }
    }, [events, autoScroll]);

    const filteredEvents = selectedType
        ? events.filter(e => e.type === selectedType)
        : events;

    const eventTypes = Array.from(new Set(events.map(e => e.type)));

    const toggleEvent = (id: string) => {
        setExpandedEvents(prev => {
            const next = new Set(prev);
            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }
            return next;
        });
    };

    const formatTimestamp = (date: Date) => {
        return date.toLocaleTimeString("en-US", {
            hour12: false,
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            fractionalSecondDigits: 3,
        });
    };

    const getEventColor = (type: string) => {
        return eventColorMap[type] || "#6b7280";
    };

    return (
        <div
            className={`debug-panel ${className}`}
            style={{
                position: isPinned ? "fixed" : "relative",
                bottom: isPinned ? "16px" : "auto",
                right: isPinned ? "16px" : "auto",
                width: isPinned ? "480px" : "100%",
                maxWidth: "100%",
                zIndex: 9999,
                fontFamily: "var(--font-geist-mono, monospace)",
                fontSize: "12px",
            }}
        >
            <div
                style={{
                    background: "linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%)",
                    borderRadius: "12px",
                    border: "1px solid rgba(148, 163, 184, 0.15)",
                    boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05)",
                    backdropFilter: "blur(20px)",
                    overflow: "hidden",
                }}
            >
                {/* Header */}
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "12px 16px",
                        borderBottom: isOpen ? "1px solid rgba(148, 163, 184, 0.1)" : "none",
                        background: "linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%)",
                    }}
                >
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            style={{
                                background: "transparent",
                                border: "none",
                                cursor: "pointer",
                                padding: "4px",
                                display: "flex",
                                alignItems: "center",
                                color: "#94a3b8",
                                transition: "transform 0.2s ease",
                                transform: isOpen ? "rotate(0deg)" : "rotate(-90deg)",
                            }}
                            aria-label={isOpen ? "Collapse" : "Expand"}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M6 9l6 6 6-6" />
                            </svg>
                        </button>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <div
                                style={{
                                    width: "8px",
                                    height: "8px",
                                    borderRadius: "50%",
                                    background: events.length > 0 ? "#22c55e" : "#6b7280",
                                    boxShadow: events.length > 0 ? "0 0 8px #22c55e" : "none",
                                    animation: events.length > 0 ? "pulse 2s infinite" : "none",
                                }}
                            />
                            <span style={{ color: "#f1f5f9", fontWeight: 600, letterSpacing: "0.025em" }}>
                                Debug Panel
                            </span>
                            <span
                                style={{
                                    background: "rgba(59, 130, 246, 0.2)",
                                    color: "#60a5fa",
                                    padding: "2px 8px",
                                    borderRadius: "9999px",
                                    fontSize: "10px",
                                    fontWeight: 500,
                                }}
                            >
                                {events.length} events
                            </span>
                        </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <button
                            onClick={() => setAutoScroll(!autoScroll)}
                            style={{
                                background: autoScroll ? "rgba(59, 130, 246, 0.2)" : "transparent",
                                border: "1px solid " + (autoScroll ? "rgba(59, 130, 246, 0.4)" : "rgba(148, 163, 184, 0.2)"),
                                borderRadius: "6px",
                                padding: "6px 10px",
                                cursor: "pointer",
                                color: autoScroll ? "#60a5fa" : "#94a3b8",
                                fontSize: "10px",
                                fontWeight: 500,
                                transition: "all 0.2s ease",
                            }}
                            title="Toggle auto-scroll"
                        >
                            {autoScroll ? "⬇️ Auto" : "⏸️ Paused"}
                        </button>
                        <button
                            onClick={() => setIsPinned(!isPinned)}
                            style={{
                                background: isPinned ? "rgba(168, 85, 247, 0.2)" : "transparent",
                                border: "1px solid " + (isPinned ? "rgba(168, 85, 247, 0.4)" : "rgba(148, 163, 184, 0.2)"),
                                borderRadius: "6px",
                                padding: "6px",
                                cursor: "pointer",
                                color: isPinned ? "#a855f7" : "#94a3b8",
                                transition: "all 0.2s ease",
                                display: "flex",
                                alignItems: "center",
                            }}
                            title={isPinned ? "Unpin" : "Pin to corner"}
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M12 2v20M2 12h20" strokeLinecap="round" />
                            </svg>
                        </button>
                        <button
                            onClick={clearEvents}
                            style={{
                                background: "rgba(239, 68, 68, 0.1)",
                                border: "1px solid rgba(239, 68, 68, 0.3)",
                                borderRadius: "6px",
                                padding: "6px 10px",
                                cursor: "pointer",
                                color: "#f87171",
                                fontSize: "10px",
                                fontWeight: 500,
                                transition: "all 0.2s ease",
                            }}
                            title="Clear all events"
                        >
                            Clear
                        </button>
                    </div>
                </div>

                {/* Content */}
                {isOpen && (
                    <>
                        {/* Filter bar */}
                        {eventTypes.length > 0 && (
                            <div
                                style={{
                                    display: "flex",
                                    flexWrap: "wrap",
                                    gap: "6px",
                                    padding: "12px 16px",
                                    borderBottom: "1px solid rgba(148, 163, 184, 0.1)",
                                    background: "rgba(0, 0, 0, 0.2)",
                                }}
                            >
                                <button
                                    onClick={() => setSelectedType(null)}
                                    style={{
                                        background: selectedType === null ? "rgba(255, 255, 255, 0.1)" : "transparent",
                                        border: "1px solid " + (selectedType === null ? "rgba(255, 255, 255, 0.2)" : "rgba(148, 163, 184, 0.15)"),
                                        borderRadius: "6px",
                                        padding: "4px 10px",
                                        cursor: "pointer",
                                        color: selectedType === null ? "#f1f5f9" : "#94a3b8",
                                        fontSize: "10px",
                                        fontWeight: 500,
                                        transition: "all 0.2s ease",
                                    }}
                                >
                                    All
                                </button>
                                {eventTypes.map((type) => (
                                    <button
                                        key={type}
                                        onClick={() => setSelectedType(selectedType === type ? null : type)}
                                        style={{
                                            background: selectedType === type ? `${getEventColor(type)}20` : "transparent",
                                            border: `1px solid ${selectedType === type ? getEventColor(type) + "60" : "rgba(148, 163, 184, 0.15)"}`,
                                            borderRadius: "6px",
                                            padding: "4px 10px",
                                            cursor: "pointer",
                                            color: selectedType === type ? getEventColor(type) : "#94a3b8",
                                            fontSize: "10px",
                                            fontWeight: 500,
                                            transition: "all 0.2s ease",
                                        }}
                                    >
                                        {type}
                                    </button>
                                ))}
                            </div>
                        )}

                        {/* Event list */}
                        <div
                            ref={eventListRef}
                            style={{
                                maxHeight: isPinned ? "400px" : "300px",
                                overflowY: "auto",
                                overflowX: "hidden",
                            }}
                        >
                            {filteredEvents.length === 0 ? (
                                <div
                                    style={{
                                        padding: "40px 16px",
                                        textAlign: "center",
                                        color: "#64748b",
                                    }}
                                >
                                    <div style={{ fontSize: "24px", marginBottom: "8px" }}>📡</div>
                                    <div style={{ fontWeight: 500 }}>Waiting for events...</div>
                                    <div style={{ fontSize: "10px", marginTop: "4px", opacity: 0.7 }}>
                                        Interact with the agent to see streamed events
                                    </div>
                                </div>
                            ) : (
                                filteredEvents.map((event, index) => (
                                    <div
                                        key={event.id}
                                        style={{
                                            borderBottom: index < filteredEvents.length - 1 ? "1px solid rgba(148, 163, 184, 0.05)" : "none",
                                            background: index % 2 === 0 ? "transparent" : "rgba(0, 0, 0, 0.1)",
                                            transition: "background 0.15s ease",
                                        }}
                                    >
                                        <div
                                            onClick={() => toggleEvent(event.id)}
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                                padding: "10px 16px",
                                                cursor: "pointer",
                                                gap: "12px",
                                            }}
                                            onMouseEnter={(e) => {
                                                e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)";
                                            }}
                                            onMouseLeave={(e) => {
                                                e.currentTarget.style.background = "transparent";
                                            }}
                                        >
                                            <button
                                                style={{
                                                    background: "transparent",
                                                    border: "none",
                                                    cursor: "pointer",
                                                    padding: "0",
                                                    color: "#64748b",
                                                    fontSize: "10px",
                                                    transition: "transform 0.2s ease",
                                                    transform: expandedEvents.has(event.id) ? "rotate(90deg)" : "rotate(0)",
                                                }}
                                            >
                                                ▶
                                            </button>
                                            <span
                                                style={{
                                                    color: "#64748b",
                                                    fontSize: "10px",
                                                    fontVariantNumeric: "tabular-nums",
                                                    minWidth: "80px",
                                                }}
                                            >
                                                {formatTimestamp(event.timestamp)}
                                            </span>
                                            <span
                                                style={{
                                                    background: `${getEventColor(event.type)}15`,
                                                    color: getEventColor(event.type),
                                                    padding: "2px 8px",
                                                    borderRadius: "4px",
                                                    fontSize: "10px",
                                                    fontWeight: 600,
                                                    letterSpacing: "0.025em",
                                                    border: `1px solid ${getEventColor(event.type)}30`,
                                                }}
                                            >
                                                {event.type}
                                            </span>
                                        </div>
                                        {expandedEvents.has(event.id) && (
                                            <div
                                                style={{
                                                    padding: "12px 16px 16px 48px",
                                                    background: "rgba(0, 0, 0, 0.3)",
                                                    borderTop: "1px solid rgba(148, 163, 184, 0.05)",
                                                }}
                                            >
                                                <pre
                                                    style={{
                                                        margin: 0,
                                                        padding: "12px",
                                                        background: "rgba(0, 0, 0, 0.4)",
                                                        borderRadius: "8px",
                                                        color: "#e2e8f0",
                                                        fontSize: "11px",
                                                        lineHeight: 1.5,
                                                        overflow: "auto",
                                                        maxHeight: "200px",
                                                        border: "1px solid rgba(148, 163, 184, 0.1)",
                                                    }}
                                                >
                                                    {JSON.stringify(event.data, null, 2)}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </>
                )}
            </div>

            {/* Pulse animation */}
            <style jsx global>{`
        @keyframes pulse {
          0% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
          100% {
            opacity: 1;
          }
        }
        
        .debug-panel::-webkit-scrollbar {
          width: 6px;
        }
        
        .debug-panel::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .debug-panel::-webkit-scrollbar-thumb {
          background: rgba(148, 163, 184, 0.2);
          border-radius: 3px;
        }
        
        .debug-panel::-webkit-scrollbar-thumb:hover {
          background: rgba(148, 163, 184, 0.3);
        }
      `}</style>
        </div>
    );
}
