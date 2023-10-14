import os
import time
import importlib
import multiprocessing

from arb_logger.logger import get_logger

from arb_sysload.base_check import BaseCheck

LOGGER = get_logger('arb_sysload', short=True)


class ArbSysload:

    def __init__(self):
        self.checks = []

    def load_checks_from_directory(self):
        directory = os.path.dirname(os.path.abspath(__file__)) + "/checks"

        LOGGER.info(f"Loading checks from directory {directory}")

        # List all .py files in the directory
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]  # Strip off .py
                module = importlib.import_module(
                    f"arb_sysload.checks.{module_name}")

                # Instantiate classes that are subclass of BaseCheck
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(
                            attr, BaseCheck) and attr is not BaseCheck:
                        check_class = attr
                        self.register_check(check_class)

        LOGGER.info(f"Loaded {len(self.checks)} checks")

    def register_check(self, check_class):
        LOGGER.info(f"Registering check {check_class.__name__}")
        self.checks.append(check_class)

    def run_check(self, check_class):
        check = check_class()
        while True:
            LOGGER.info(f"Running check {check.name}")
            status = check.execute()
            LOGGER.info(
                f"Check {check.name} finished with status {status}, sleeping for {check.INTERVAL} seconds"
            )
            time.sleep(check.INTERVAL)

    def start(self):
        LOGGER.info("Starting checks")

        processes = []
        for check_class in self.checks:
            p = multiprocessing.Process(target=self.run_check,
                                        args=(check_class, ))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()


def main():
    LOGGER.info("Starting arb sysload")
    arb_sysload = ArbSysload()

    arb_sysload.load_checks_from_directory()
    arb_sysload.start()


if __name__ == "__main__":
    main()
