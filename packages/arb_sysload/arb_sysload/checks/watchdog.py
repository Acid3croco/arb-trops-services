import redis
from arb_sysload.base_check import BaseCheck


class WatchdogCheck(BaseCheck):
    INTERVAL = 15  # adjust as needed

    def run(self):
        down_processes = []

        # Get the list of all keys matching the pattern
        keys = self.redis.keys('arb_watchdog:*')

        # Check which expected processes are missing
        for key in keys:
            status = self.redis.hget(key, 'status')
            print(status)
            if status != "UP":
                process = key.split(":")[1]
                down_processes.append(process)

        # Construct the message
        message = "All processes are present. "
        if down_processes:
            message = f"Processes marked as down: {', '.join(down_processes)}."

        # Update status based on missing or down processes
        if down_processes:
            self.error(message)
        else:
            self.success(message)
