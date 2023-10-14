# ArbSysload

`ArbSysload` is a flexible and extendable system load monitoring tool built using Flask and Redis. It provides real-time system check results via an API and stores check outcomes in Redis.

## Features

- Dynamic check registration.
- Concurrency support for executing checks via multiprocessing.
- RESTful API to retrieve the check results and perform actions.
- Built-in support for custom user interactions like muting, disabling, or relaunching checks.

## Installation

Clone the repository and install using `setup.py`:

```bash
git clone [repository_url]
cd packages/arb_sysload
pip install -e ./  # Install in editable mode
```

## Usage

> One can use [arb_launcher](../../packages/arb_launcher/README.md) to launch them in the background.

### Running the Check System

```bash
arb_sysload
```

### Starting the Flask API

```bash
sysload_api
```

### API Endpoints

1. Retrieve all checks: `GET /checks`
2. Perform actions on a check: `POST /check/<check_name>/action`

## Adding a New Check

To add a new check:

1. Create a new Python module inside the `checks/` directory.
2. In this module, define a new check class that inherits from `BaseCheck`.
3. Implement the `run` method for your check.

### Example

Adding a simple check to monitor disk usage:

1. Create a file `checks/disk_usage.py`.

```python
import shutil

from arb_sysload.base_check import BaseCheck


class DiskUsageCheck(BaseCheck):
    INTERVAL = 300  # Custom interval, run every 5 minutes

    MIN_SIZE_GB = 100

    def run(self):
        total, used, free = shutil.disk_usage("/")

        # Let's say we consider it a failure if less than 10GB is free
        if free < self.MIN_SIZE_GB * (1024**3):  # 10 GB in bytes
            self.error(f"Only {free / (1024 ** 3)} GB free space left!")
        else:
            self.success(f"{free / (1024 ** 3)} GB free space available.")

```

2. Once you've added your check, `arb_sysload.py` will automatically load and execute it based on its interval.
