from dataclasses import dataclass
from enum import Enum, auto
from typing import Set
import time

class EventType(Enum):
    KEYBOARD = auto()
    TRACKPAD = auto()
    SYSTEM = auto()

class KeyAction(Enum):
    DOWN = auto()
    UP = auto()

class Modifier(Enum):
    CMD = auto()
    SHIFT = auto()
    CTRL = auto()
    ALT = auto()

class TrackpadAction(Enum):
    MOVE = auto()
    CLICK_DOWN = auto()
    CLICK_UP = auto()
    SCROLL = auto()

class SystemCommand(Enum):
    LOCK_SCREEN = auto()
    SLEEP = auto()
    SHOW_POWER_DIALOG = auto()

@dataclass(frozen=True)
class BaseEvent:
    event_type: EventType
    timestamp: float

@dataclass(frozen=True)
class KeyboardEvent(BaseEvent):
    key: str
    action: KeyAction
    modifiers: Set[Modifier]

@dataclass(frozen=True)
class TrackpadEvent(BaseEvent):
    action: TrackpadAction
    dx: float = 0.0
    dy: float = 0.0

@dataclass(frozen=True)
class SystemCommandEvent(BaseEvent):
    command: SystemCommand

