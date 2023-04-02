# arb_watchdog

`arb_watchdog` is a Python package designed to monitor and manage the status of specified processes. It uses Redis as a backend for storing process data and provides a simple API for interacting with this data. The package is highly configurable and can be used to monitor and manage a wide range of processes.

## Features

- Monitor the status of specified processes
- Store process data in Redis
- Configurable process monitoring interval
- Automatically reloads configuration when the config file is updated
- Supports multiple processes
- Provides a simple API for interacting with process data

## Installation

To install the `arb_watchdog` package, you can use `pip`:

```bash
pip install arb_watchdog
```

## Config File

First, create a configuration file in JSON format with the following keys:

- `redis_host`: The hostname of your Redis server (e.g., "localhost")
- `redis_port`: The port number of your Redis server (e.g., 6379)
- `interval`: The interval (in seconds) at which the processes will be monitored (e.g., 60)
- `processes`: A list of process names to monitor (e.g., ["fake_process", "another_fake_process"])

Example configuration file (config.json):

```json
{
  "redis_host": "localhost",
  "redis_port": 6379,
  "interval": 60,
  "processes": ["fake_process", "another_fake_process"]
}
```

> By default, `arb_watchdog` will look for a configuration file under the `$ARB_CONFIGS_PATH` directory. (`$ARB_CONFIGS_PATH/arb_watchdog_config.json`). If this variable is not set, it will use `./arb_watchdog_config.json`.

# Usage

To use `arb_watchdog`, import the package and create a `ProcessWatcher` instance with the path to your configuration file:

```python
from arb_watchdog.process_watcher import ProcessWatcher

config_file = "config.json"
process_watcher = ProcessWatcher(config_file=config_file)
```

You can then use the `ProcessWatcher` instance to perform various operations, such as getting the process list, updating process data, and getting process data for specified processes:

```python
# Get the list of processes to monitor
process_list = process_watcher.get_process_list()

# Update process data
process_data = ProcessData(name="fake_process", pid=12345, status="UP")
process_watcher.update_process_data(process_data)

# Get process data for a specified process
process_data = process_watcher.get_process_data("fake_process")
```

## Console Scripts

`arb_watchdog` provides two console scripts for easy interaction with the package: `arb_watchdog` and `arb_watchdog_cli`.

### arb_watchdog

`arb_watchdog` is a console script that runs the `arb_watchdog` process in the background, continuously monitoring the specified processes and updating their data in Redis. To run the script, simply execute the following command in your terminal, replacing <config_file> with the path to your configuration file:

```bash
arb_watchdog -f <config_file>
```

### arb_watchdog_cli

`arb_watchdog_cli` is a console script that shows data stored in the Redis database based on the `config.json` file

To run the script, execute the following command in your terminal, replacing <config_file> with the path to your configuration file:

```bash
arb_watchdog_cli -f <config_file>
```

Example output:

![Example arb_watchdog_cli](https://cdn.discordapp.com/attachments/1035680942137819226/1092040305936703618/image.png)

## Running Tests

To run the tests for the `arb_watchdog` package, use the following command:

```bash
python -m unittest discover -s tests
```
