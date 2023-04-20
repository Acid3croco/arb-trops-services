from arb_launcher.program_handler import ProgramHandler


def launch_detached(command,
                    args=None,
                    stdout=None,
                    stderr=None,
                    kill_previous=True):
    program_handler = ProgramHandler(command, args, stdout, stderr)
    program_handler.launch(kill_previous=kill_previous)
