import docker

from arb_sysload.base_check import BaseCheck


class DockerCheck(BaseCheck):
    INTERVAL = 60  # Run every 60 seconds
    EXPECTED_CONTAINERS = {
        "arb_trops_web", "crypto_dashboard_backend", "cryptools",
        "crypto_dashboard_redis", "crypto_dashboard_database", "arb_trops_db",
        "arb_trops_grafana"
    }  # Example expected container names

    def run(self):
        client = docker.from_env()

        running_containers = set(container.name
                                 for container in client.containers.list())

        # Determine missing containers
        missing_containers = self.EXPECTED_CONTAINERS - running_containers

        # Construct the message
        if missing_containers:
            message = f"Missing containers: {', '.join(missing_containers)}"
            self.error(message)
        else:
            message = "All expected containers are running."
            self.success(message)
