from datetime import datetime
import random
import json
from typing import Dict, Any, TypeVar, Optional
from dataclasses import is_dataclass, asdict
from .hex import Hex

T = TypeVar('T')

def generate_id(prefix: str = '') -> str:
    """Generate a random ID with optional prefix"""
    return f"{prefix}{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def serialize_game_state(state: Any) -> Dict[str, Any]:
    """
    Recursively serialize game state to dict
    Handles dataclasses, dicts, lists, and Hex objects
    """
    if is_dataclass(state):
        return {k: serialize_game_state(v) for k, v in asdict(state).items()}
    elif isinstance(state, dict):
        return {k: serialize_game_state(v) for k, v in state.items()}
    elif isinstance(state, (list, tuple)):
        return [serialize_game_state(item) for item in state]
    elif isinstance(state, Hex):
        return {'q': state.q, 'r': state.r}
    return state

def validate_move(start: Hex, end: Hex, max_distance: int = 1) -> bool:
    """Validate hex movement distance"""
    return start.distance_to(end) <= max_distance

def log_game_event(event: str, data: Optional[Dict[str, Any]] = None):
    """
    Log game events with structured data
    Example output:
    {
        "timestamp": "2023-07-20T14:30:00.000000",
        "event": "tank_moved",
        "data": {"tank_id": 1, "from": {"q": 0, "r": 0}, "to": {"q": 1, "r": 0}}
    }
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event': event,
        'data': data or {}
    }
    print(json.dumps(log_entry, indent=2))  # Pretty-print for readability

def clamp(value: T, min_val: T, max_val: T) -> T:
    """Restrict value between min and max bounds"""
    return max(min_val, min(value, max_val))