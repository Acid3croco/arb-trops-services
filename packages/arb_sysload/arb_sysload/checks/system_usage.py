import psutil

from arb_sysload.base_check import BaseCheck


class SystemUsageCheck(BaseCheck):
    INTERVAL = 15  # Run every 15 seconds

    def run(self):
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        # Load average
        load_avg_1, load_avg_5, load_avg_15 = psutil.getloadavg()
        # RAM usage
        ram = psutil.virtual_memory()

        # Construct the message
        message = ' - '.join([
            f"CPU: {cpu_percent}%",
            f"LA: {load_avg_1:.2f} {load_avg_5:.2f} {load_avg_15:.2f}",
            f"RAM: {ram.percent}%"
        ])

        # In this example, we'll assume that a CPU usage of over 90% or RAM usage over 90% is an error.
        if cpu_percent > 90 or ram.percent > 95:
            self.error(message)
        elif cpu_percent > 80 or ram.percent > 90:
            self.warning(message)
        else:
            self.success(message)
