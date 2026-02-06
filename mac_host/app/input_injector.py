import Quartz
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    CGEventCreateMouseEvent,
    CGEventCreateScrollWheelEvent,
    kCGEventKeyDown,
    kCGEventKeyUp,
    kCGEventMouseMoved,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventScrollWheel,
    kCGHIDEventTap,
    kCGMouseButtonLeft,
)

from shared.protocol.events import (
    KeyboardEvent,
    TrackpadEvent,
    SystemCommandEvent,
    Modifier,
    KeyAction,
    TrackpadAction,
    SystemCommand,
)


# -----------------------------
# Modifier mapping (protocol → macOS)
# -----------------------------

MODIFIER_FLAGS = {
    Modifier.CMD: Quartz.kCGEventFlagMaskCommand,
    Modifier.SHIFT: Quartz.kCGEventFlagMaskShift,
    Modifier.CTRL: Quartz.kCGEventFlagMaskControl,
    Modifier.ALT: Quartz.kCGEventFlagMaskAlternate,
}


# -----------------------------
# Keyboard injection
# -----------------------------

def inject_keyboard_event(event: KeyboardEvent) -> None:
    keycode = key_to_keycode(event.key)
    is_down = event.action == KeyAction.DOWN

    cg_event = CGEventCreateKeyboardEvent(
        None,
        keycode,
        is_down,
    )

    flags = 0
    for mod in event.modifiers:
        flags |= MODIFIER_FLAGS.get(mod, 0)

    CGEventSetFlags(cg_event, flags)
    CGEventPost(kCGHIDEventTap, cg_event)


# -----------------------------
# Trackpad / mouse injection
# -----------------------------

def inject_trackpad_event(event: TrackpadEvent) -> None:
    if event.action == TrackpadAction.MOVE:
        mouse_event = CGEventCreateMouseEvent(
            None,
            kCGEventMouseMoved,
            current_mouse_position(event.dx, event.dy),
            kCGMouseButtonLeft,
        )
        CGEventPost(kCGHIDEventTap, mouse_event)

    elif event.action == TrackpadAction.CLICK_DOWN:
        click_event = CGEventCreateMouseEvent(
            None,
            kCGEventLeftMouseDown,
            current_mouse_position(0, 0),
            kCGMouseButtonLeft,
        )
        CGEventPost(kCGHIDEventTap, click_event)

    elif event.action == TrackpadAction.CLICK_UP:
        click_event = CGEventCreateMouseEvent(
            None,
            kCGEventLeftMouseUp,
            current_mouse_position(0, 0),
            kCGMouseButtonLeft,
        )
        CGEventPost(kCGHIDEventTap, click_event)

    elif event.action == TrackpadAction.SCROLL:
        scroll_event = CGEventCreateScrollWheelEvent(
            None,
            kCGEventScrollWheel,
            2,
            int(event.dy),
            int(event.dx),
        )
        CGEventPost(kCGHIDEventTap, scroll_event)


# -----------------------------
# System command handling
# -----------------------------

def handle_system_command(event: SystemCommandEvent) -> None:
    if event.command == SystemCommand.LOCK_SCREEN:
        Quartz.CGSessionLock()

    elif event.command == SystemCommand.SLEEP:
        Quartz.CGSessionSleep()

    elif event.command == SystemCommand.SHOW_POWER_DIALOG:
        Quartz.CGEventPost(
            kCGHIDEventTap,
            CGEventCreateKeyboardEvent(None, 0x7F, True),
        )


# -----------------------------
# Helpers
# -----------------------------

def key_to_keycode(key: str) -> int:
    """
    VERY minimal mapping for v0.
    This WILL expand later.
    """
    key = key.upper()

    mapping = {
        "A": 0x00,
        "S": 0x01,
        "D": 0x02,
        "F": 0x03,
        "H": 0x04,
        "G": 0x05,
        "Z": 0x06,
        "X": 0x07,
        "C": 0x08,
        "V": 0x09,
        "B": 0x0B,
        "Q": 0x0C,
        "W": 0x0D,
        "E": 0x0E,
        "R": 0x0F,
        "Y": 0x10,
        "T": 0x11,
        "ENTER": 0x24,
        "SPACE": 0x31,
    }

    if key not in mapping:
        raise ValueError(f"Unsupported key: {key}")

    return mapping[key]


def current_mouse_position(dx: float, dy: float):
    loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
    return Quartz.CGPointMake(loc.x + dx, loc.y + dy)