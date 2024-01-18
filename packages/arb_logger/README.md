# arb_logger

## Introduction

`arb_logger` is a Python package that provides advanced logging capabilities, including file logging, console logging with colors, and Redis integration. This package aims to simplify and standardize logging for Python applications by offering an easy-to-use interface and configurable options.

## Features

- Colored console logging
- Logging to file with optional log rotation
- Logging to Redis using streams
- Custom log level for STDOUT
- Uncaught exceptions logging
- Customizable log format
- Unit tests for key functionality
- `arb_alerts` program to listen to Redis streams and send alerts on MacOS

## Installation

To install the `arb_logger` package from PyPI, simply run the following command:

```bash
pip install arb_logger
```

To install the `arb_logger` package from source, simply clone the repository and install it using `pip`:

```bash
git clone https://github.com/acid3croco/arb_logger.git
cd arb_logger
pip install .
```

## Usage

### Basic Usage

Here's an example of how to create a logger with default settings:

```python
from arb_logger import get_logger

# The name of the logger will be the name of the calling module
# if you call the logger from the main module (i.e. __name__ == "__main__")
# you have to specify the name of the logger, if you call it from a module
# the name of the logger will be the name of the module automatically
logger = get_logger('basic_logger')

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Advanced Usage

In this example, we create a logger with custom settings:

```python
from pathlib import Path
from arb_logger import get_logger

custom_path = Path("custom_logs")
logger = get_logger(name="my_logger", level=logging.DEBUG, path=custom_path,
                    log_in_file=True, short=False, redis_handler=True)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Code documentation

### get_logger

`get_logger` is the main function used to create a logger with custom settings.

```python
def get_logger(name: str = None,
               level: int = logging.DEBUG,
               path: Path = None,
               log_in_file: bool = True,
               short: bool = False,
               redis_handler: bool = True,
               custom_redis_client: Redis = None) -> logging.Logger:
```

#### Parameters

- `name`: The name of the logger. Defaults to the name of the calling module.
- `level`: The minimum log level to log messages. Defaults to logging.DEBUG.
- `path`: The directory where log files will be saved. Defaults to None, which means the default log directory will be used.
- `log_in_file`: Whether to log messages to a file. Defaults to True.
- `short`: Whether to use a short log filename without the process ID. Defaults to False.
- `redis_handler`: Whether to use a Redis handler for logging. Defaults to True.
- `custom_redis_client`: A custom Redis client to use for logging. Defaults to None, which means a new Redis client will be created using the `get_redis_log_client()` method inside `logger.py`.

#### Returns

A logger with the specified settings.

---

## arb_alerts

`arb_alerts` is a script that listens for log messages from a Redis channel and processes them. It logs the messages to a local logger and sends macOS notifications for messages with log level ERROR or higher.

### Features

```bash
arb_alerts
```

- Listens for log messages on a Redis channel.
- Logs the messages to a local logger.
- Sends macOS notifications for messages with log level ERROR or higher.
