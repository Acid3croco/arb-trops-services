import os
import subprocess

from pathlib import Path

from arb_sysload.base_check import BaseCheck


class MassifApiException(BaseCheck):

    def _get_last_extractor_log(self):
        # log file is $ARB_LOGS_PATH/extractor_api.$(date +%y-%m-%d-%H-%M-%S).log in a shell script
        log_path = os.getenv("ARB_LOGS_PATH")

        files = Path(log_path).glob("extractor_api.*.log")
        latest_file = max([f for f in files],
                          key=lambda item: item.stat().st_ctime)
        return latest_file.absolute()

    def run(self):
        log_file_path = self._get_last_extractor_log()
        try:
            # Run grep to search for "Exception" in the log file
            result = subprocess.run(
                ["grep", "Exception", log_file_path], text=True, capture_output=True)

            if result.returncode == 0:  # grep found 'Exception'
                self.error(
                    f"Found 'Exception' in log file: {log_file_path}")
            elif result.returncode == 1:  # grep did not find 'Exception'
                self.success(
                    f"No 'Exception' found")
            else:
                # An error occurred in grep
                self.error(f"Error checking log file: {result.stderr}")
        except Exception as e:
            # Handle any exception that occurred during the process
            self.error(f"Exception occurred while checking log file: {str(e)}")
