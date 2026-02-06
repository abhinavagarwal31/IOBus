import asyncio
import json
import time

from .config import HOST, PORT

from shared.protocol.events import (
    EventType,
    KeyAction,
    Modifier,
    TrackpadAction,
    SystemCommand,
    BaseEvent,
    KeyboardEvent,
    TrackpadEvent,
    SystemCommandEvent,
)

from .input_injector import (
    inject_keyboard_event,
    inject_trackpad_event,
    handle_system_command,
)


# -----------------------------
# Event Parsing (JSON → Objects)
# -----------------------------

def parse_event(data: dict) -> BaseEvent:
    """
    Convert raw JSON dict into a strongly-typed Event object.
    This is the trust boundary of the system.
    """

    event_type = EventType[data["event_type"]]
    timestamp = data.get("timestamp", time.time())

    if event_type == EventType.KEYBOARD:
        return KeyboardEvent(
            event_type=event_type,
            timestamp=timestamp,
            key=data["key"],
            action=KeyAction[data["action"]],
            modifiers={Modifier[m] for m in data.get("modifiers", [])},
        )

    elif event_type == EventType.TRACKPAD:
        return TrackpadEvent(
            event_type=event_type,
            timestamp=timestamp,
            action=TrackpadAction[data["action"]],
            dx=data.get("dx", 0.0),
            dy=data.get("dy", 0.0),
        )

    elif event_type == EventType.SYSTEM:
        return SystemCommandEvent(
            event_type=event_type,
            timestamp=timestamp,
            command=SystemCommand[data["command"]],
        )

    else:
        raise ValueError(f"Unsupported event type: {event_type}")


# -----------------------------
# Event Routing (Execution Layer)
# -----------------------------

def handle_event(event: BaseEvent) -> None:
    """
    Route events to macOS input injection.
    """

    if isinstance(event, KeyboardEvent):
        inject_keyboard_event(event)

    elif isinstance(event, TrackpadEvent):
        inject_trackpad_event(event)

    elif isinstance(event, SystemCommandEvent):
        handle_system_command(event)

    else:
        print(f"[UNKNOWN EVENT] {event}")


# -----------------------------
# Client Connection Handler
# -----------------------------

async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    addr = writer.get_extra_info("peername")
    print(f"[CONNECTED] {addr}")

    try:
        while True:
            line = await reader.readline()
            if not line:
                break

            message = line.decode().strip()
            data = json.loads(message)

            event = parse_event(data)
            handle_event(event)

    except Exception as e:
        print(f"[ERROR] {addr} → {e}")

    finally:
        print(f"[DISCONNECTED] {addr}")
        writer.close()
        await writer.wait_closed()


# -----------------------------
# Server Bootstrap
# -----------------------------

async def main() -> None:
    server = await asyncio.start_server(handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    print(f"[STARTED] IOBus Mac Host listening on {addr}")

    async with server:
        await server.serve_forever()


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server stopped")