# arb_launcher

`arb_launcher` is a Python package that provides a simple yet powerful way to launch and manage detached programs and methods. It allows you to run external programs or Python methods in a completely detached process, making them independent of the parent process.

## Features

- Launch external programs and Python methods as detached processes
- Redirect the `stdout` and `stderr` of the detached process to specific files (`/dev/null` by default so that the output is never printed to the console)
- Terminate matching processes based on their names and arguments
- Fully daemonized processes, making them independent of the parent process and allowing them to run in the background

## Installation

To install `arb_launcher`, simply clone the repository and run the following command:

```bash
pip install arb_launcher
```

## Usage

`arb_launcher` provides a simple command-line interface for launching detached programs. You can also use it as a method or library in your Python projects.

### Command-Line Interface

To use the command-line interface, simply run:

```bash
arb_launcher <program> [args] [--stdout <stdout_file>] [--stderr <stderr_file>]
```

### Simplified Launch Method

The `arb_launcher` package also provides a simplified method, `launch_detached`, for quickly launching detached programs or methods:

```python
from arb_launcher.launcher import launch_detached

launch_detached(target, args, stdout=None, stderr=None)
```

`target` can be either a string representing the command or a callable Python method.

`args` should be a list of arguments, if any.

`stdout` and `stderr` are optional parameters to redirect the output to specific files.

#### Example

Here's an example of how to use the simplified `launch_detached` method to launch a detached Python method:

```python
from arb_launcher.launcher import launch_detached

def my_method(arg1, arg2):
    # Your code here

launch_detached(my_method, args=['arg1', 'arg2'], stdout='output.log', stderr='error.log')
```

### Python API

To use the `arb_launcher` package in your Python project, first import the `ProgramHandler` class:

```python
from arb_launcher.program_handler import ProgramHandler
```

Then, create a `ProgramHandler` object and call the `launch()` method:

```python
handler = ProgramHandler(target, args, stdout, stderr)
handler.launch()
```

`target` can be either a string representing the command or a callable Python method.

`args` should be a list of arguments, if any.

`stdout` and `stderr` are optional parameters to redirect the output to specific files.

#### Example

Here's an example of how to use the `arb_launcher` package to launch a detached Python method:

```python
from arb_launcher.program_handler import ProgramHandler

def my_method(arg1, arg2):
    # Your code here

handler = ProgramHandler(my_method, args=['arg1', 'arg2'], stdout='output.log', stderr='error.log')
handler.launch()
```
