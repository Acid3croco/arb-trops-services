import subprocess

from arb_sysload.base_check import BaseCheck


class MassifApiException(BaseCheck):
    LOG_FILE_PATH = "/home/jack/Trading/massif-extractor/massif-extractor-back/packages/massif_extractor_api/bin/extractor_api.log"

    def run(self):
        try:
            # Run grep to search for "Exception" in the log file
            result = subprocess.run(
                ["grep", "Exception", self.LOG_FILE_PATH], text=True, capture_output=True)

            if result.returncode == 0:  # grep found 'Exception'
                self.error(
                    f"Found 'Exception' in log file: {self.LOG_FILE_PATH}")
            elif result.returncode == 1:  # grep did not find 'Exception'
                self.success(
                    f"No 'Exception' found in log file: {self.LOG_FILE_PATH}")
            else:
                # An error occurred in grep
                self.error(f"Error checking log file: {result.stderr}")
        except Exception as e:
            # Handle any exception that occurred during the process
            self.error(f"Exception occurred while checking log file: {str(e)}")
