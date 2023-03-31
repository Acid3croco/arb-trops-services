from types import TracebackType
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class LogMessage:
    name: str
    msg: str
    levelno: Optional[int | str] = 'INFO'
    args: Optional[Tuple[Any, ...]] = None
    levelname: Optional[str] = None
    pathname: Optional[str] = None
    filename: Optional[str] = None
    module: Optional[str] = None
    exc_info: Optional[Tuple[type, BaseException, TracebackType]] = None
    exc_text: Optional[str] = None
    stack_info: Optional[str] = None
    lineno: Optional[int] = None
    funcName: Optional[str] = None
    created: Optional[float] = None
    msecs: Optional[float] = None
    relativeCreated: Optional[float] = None
    thread: Optional[int] = None
    threadName: Optional[str] = None
    processName: Optional[str] = None
    process: Optional[int] = None

    @classmethod
    def from_dict(cls, record_dict: Dict[str, Any]) -> 'LogMessage':
        return cls(**record_dict)
