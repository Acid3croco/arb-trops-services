import json

from numbers import Number
from logging import LogRecord
from dataclasses import dataclass, field, fields
from typing import Any, Dict, Optional


@dataclass
class AlertMessage:
    name: str
    msg: str
    levelno: int = 30
    levelname: str = 'WARNING'
    alert_type: str = 'logger'
    pathname: Optional[str] = None
    filename: Optional[str] = None
    module: Optional[str] = None
    lineno: Optional[int] = None
    funcName: Optional[str] = None
    created: Optional[float] = None
    processName: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, _record_dict: Dict[str, Any]) -> 'AlertMessage':
        # Create a AlertMessage instance from a dict with the matching fields
        record_dict = {
            k: v
            for k, v in _record_dict.items()
            if v is not None and k in FIELD_NAMES
        }
        log_message = cls(**record_dict)

        # Add extra data to the extra field
        # data that is not part of the AlertMessage dataclass fields
        extra_data = {
            k: v
            for k, v in _record_dict.items()
            if v is not None and k not in FIELD_NAMES
        }
        log_message.extra = extra_data

        return log_message

    @classmethod
    def log_record_to_dict(cls, log_record: LogRecord) -> Dict[str, Any]:

        def jsonify_value(value: Any) -> Any:
            if isinstance(value, (str, Number)):
                return value
            return json.dumps(value, separators=(',', ':'), default=str)

        record_dict = {
            k: jsonify_value(v)
            for k, v in log_record.__dict__.items()
            if (k not in LOG_RECORD_EXC_FIELDS and not k.startswith('_')
                and v is not None)
        }

        return record_dict


# Process constants only one time
FIELD_NAMES = {f.name for f in fields(AlertMessage)}
LOG_RECORD_EXC_FIELDS = {
    'args', 'msecs', 'process', 'relativeCreated', 'thread', 'threadName',
    'exc_info'
}
