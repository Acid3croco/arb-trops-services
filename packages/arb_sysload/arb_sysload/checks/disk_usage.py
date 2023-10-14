import shutil

from arb_sysload.base_check import BaseCheck


class DiskUsageCheck(BaseCheck):
    INTERVAL = 300  # Run every 5 minutes

    MIN_SIZE_GB = 100

    def run(self):
        total, used, free = shutil.disk_usage("/")

        # Let's say we consider it a failure if less than 10GB is free
        if free < self.MIN_SIZE_GB * (1024**3):  # 10 GB in bytes
            self.error(f"Only {free / (1024 ** 3)} GB free space left!")
        else:
            self.success(f"{free / (1024 ** 3)} GB free space available.")
