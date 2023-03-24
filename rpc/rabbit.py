from ..models.schedule import Schedule
from pylon.core.tools import web, log
from tools import task_tools, VaultClient


class RPC:
    @web.rpc('check_rabbit_queues')
    def check_rabbit_queues(self, project_id: int, task_id=None):
        vault_client = VaultClient.from_project(project_id)
        secrets = vault_client.get_project_secrets()
        hidden_secrets = vault_client.get_project_hidden_secrets()
        if task_id:
            log.info(f"check public rabbit queues")
            event = [{"user": hidden_secrets["rabbit_user"], "password": hidden_secrets["rabbit_password"],
                      "vhost": "carrier"}]
        else:
            log.info(f"check rabbit queues for project {project_id}")
            event = []

        rabbit_queue_validator_id = secrets.get("rabbit_queue_validator_id") if "rabbit_queue_validator_id" in secrets \
            else hidden_secrets.get("rabbit_queue_validator_id")
        if rabbit_queue_validator_id:
            task_tools.run_task(project_id, event, rabbit_queue_validator_id, queue_name="__internal")

    @web.rpc('create_rabbit_schedule')
    def create_rabbit_schedule(self, name, project_id, task_id=None):
        Schedule(
            name=name,
            cron="*/10 * * * *",
            active=True,
            rpc_func="check_rabbit_queues",
            rpc_kwargs={
                'project_id': project_id,
                'task_id': task_id
            }
        ).insert()

