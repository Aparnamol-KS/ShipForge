/* 
Opening the WebSocket connection for a build
Receiving build events
Passing events back to the component
Closing the connection when the component is removed
*/
import { useEffect, useRef } from "react";

interface BuildEvent {
    type: "status" | "log";
    status?: string;
    output?: string;
}

interface UseBuildWebSocketProps {
    projectId: number | null;
    buildId: number | null;
    onEvent: (event: BuildEvent) => void;
}

export function useBuildWebSocket({
    projectId,
    buildId,
    onEvent,
}: UseBuildWebSocketProps) {
    const onEventRef = useRef(onEvent);

    useEffect(() => {
        onEventRef.current = onEvent;
    }, [onEvent]);

    useEffect(() => {
        if (projectId === null || buildId === null) {
            return;
        }

        const websocket = new WebSocket(
            `ws://127.0.0.1:8000/projects/${projectId}/builds/${buildId}/ws`,
        );

        websocket.onmessage = (message) => {
            const event: BuildEvent = JSON.parse(message.data);
            onEventRef.current(event);
        };

        websocket.onerror = (error) => {
            console.error("Build WebSocket error:", error);
        };

        return () => {
            websocket.close();
        };
    }, [projectId, buildId]);
}