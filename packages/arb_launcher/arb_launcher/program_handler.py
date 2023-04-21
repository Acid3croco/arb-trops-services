import os
import shlex
import subprocess

from contextlib import redirect_stderr, redirect_stdout

import psutil

from setproctitle import setproctitle
from arb_logger.logger import get_logger

LOGGER = get_logger('arb_launcher', short=True, level='INFO')


class ProgramHandler:

    def __init__(self, target, args=None, stdout=None, stderr=None):
        self.target = target
        self.args = args
        self.stdout = stdout or '/dev/null'
        self.stderr = stderr or '/dev/null'
        self.process = None

    def launch(self, kill_previous=True):
        if kill_previous:
            self.terminate_matching_processes()

        self._launch_target()

    def _launch_target(self):
        args = self.args or []

        LOGGER.debug(f'Forking process {os.getpid()}')
        pid = os.fork()
        if pid == 0:  # Child process
            LOGGER.debug(f'Running process child {os.getpid()}')
            os.setsid()
            LOGGER.debug(f'Forking process {os.getpid()}')
            pid2 = os.fork()
            if pid2 == 0:  # Grandchild process
                LOGGER.debug(f'Running process grandchild {os.getpid()}')
                with open(self.stdout, "w") as stdout, open(self.stderr,
                                                            "w") as stderr:
                    if callable(self.target):
                        proc_name = self._get_process_name()
                        setproctitle(proc_name)
                        LOGGER.info(
                            f'Running method as process: {proc_name}, pid: {os.getpid()}'
                        )
                        with redirect_stdout(stdout), redirect_stderr(stderr):
                            self.target(*args)
                    else:
                        cmd = shlex.split(self.target)
                        if isinstance(args, str):
                            args = shlex.split(args)
                        cmd.extend(args)
                        LOGGER.info(
                            f"Running command as process: {' '.join(cmd)}")
                        #? detach the grandchild process, prevent ps showing .../arb_launcher <target>
                        #? prevered over subprocess.call, idk the consequences, maybe we spawn a lot of processes doing so
                        prc = subprocess.Popen(cmd,
                                               stdout=stdout,
                                               stderr=stderr)
                        LOGGER.info(f'Process {prc.pid} detached')
                        # subprocess.call(cmd, stdout=stdout, stderr=stderr)
                LOGGER.debug(
                    f'Process grandchlid {os.getpid()} finished, exiting')
                os._exit(0)
            else:
                # Intermediate child process exits
                LOGGER.debug(f'Process child {os.getpid()} finished, exiting')
                os._exit(0)
        else:  # Parent process
            LOGGER.debug(f'Waiting for process {os.getpid()} to finish')
            os.waitpid(pid, 0)
            LOGGER.debug(f'Process {os.getpid()} finished, exiting')

    def _get_process_name(self):
        if isinstance(self.target, str):
            return f'{self.target} {" ".join(self.args or [])}'.strip()
        elif callable(self.target):
            process = psutil.Process(os.getpid())
            process_name = process.cmdline()[0].split(' ')[0]

            filename = self.target.__code__.co_filename
            method = self.target.__name__

            _args = self.args or []
            _args = [str(arg) for arg in _args]
            _args = ' '.join(_args)

            return f'{process_name} {filename} {method}({_args})'.strip()

    def terminate_matching_processes(self):
        target_name = self._get_process_name()
        current_process = psutil.Process(os.getpid())

        LOGGER.info(f'Terminating processes with name: {target_name}')

        for process in psutil.process_iter(attrs=['cmdline', 'pid']):
            try:
                cmdline = ' '.join(process.info['cmdline'])
                if target_name in cmdline and process.pid != current_process.pid:
                    LOGGER.info(
                        f'Terminating process {process.pid} with cmdline: {cmdline}'
                    )
                    process.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied,
                    psutil.ZombieProcess) as e:
                LOGGER.warning(
                    f'Error while accessing process information: {e}')
