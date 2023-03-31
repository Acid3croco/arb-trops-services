from types import TracebackType
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class LogMessage:
    name: str
    msg: str
    args: Optional[Tuple[Any, ...]]
    levelname: str
    levelno: int
    pathname: str
    filename: str
    module: str
    exc_info: Optional[Tuple[type, BaseException, TracebackType]]
    exc_text: Optional[str]
    stack_info: Optional[str]
    lineno: int
    funcName: Optional[str]
    created: float
    msecs: float
    relativeCreated: float
    thread: int
    threadName: str
    processName: str
    process: int

    @classmethod
    def from_dict(cls, record_dict: Dict[str, Any]) -> 'LogMessage':
        return cls(args=record_dict.get('args', ()),
                   exc_info=record_dict.get('exc_info', None),
                   exc_text=record_dict.get('exc_text', None),
                   stack_info=record_dict.get('stack_info', None),
                   **record_dict)
