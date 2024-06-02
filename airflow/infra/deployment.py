import boto3

ecs_client = boto3.client("ecs")


def create_task_definition(service_name, image, cpu, memory, environment, command=None):
    container_definitions = [
        {
            "name": service_name,
            "image": image,
            "cpu": cpu,
            "memory": memory,
            "essential": True,
            "environment": environment,
            "command": command,
        }
    ]
    response = ecs_client.register_task_definition(
        family=service_name, containerDefinitions=container_definitions
    )
    return response["taskDefinition"]["taskDefinitionArn"]


# Define environment variables for each service
airflow_webserver_env = [
    {"name": "AIRFLOW__CORE__EXECUTOR", "value": "CeleryExecutor"},
    {
        "name": "AIRFLOW__CORE__SQL_ALCHEMY_CONN",
        "value": "postgresql+psycopg2://airflow:airflow@postgres/airflow",
    },
    # Add other environment variables as needed
]

flower_env = [
    {"name": "AIRFLOW__CORE__EXECUTOR", "value": "CeleryExecutor"},
    {"name": "AIRFLOW__CELERY__BROKER_URL", "value": "redis://:@redis:6379/0"},
    # Add other environment variables as needed
]

scheduler_env = [
    {"name": "AIRFLOW__CORE__EXECUTOR", "value": "CeleryExecutor"},
    # Add other environment variables as needed
]

worker_env = [
    {"name": "AIRFLOW__CORE__EXECUTOR", "value": "CeleryExecutor"},
    # Add other environment variables as needed
]

# Create task definitions for each service
airflow_webserver_task_def_arn = create_task_definition(
    service_name="airflow-webserver",
    image="${AIRFLOW_IMAGE_NAME:-parkpulse:${AIRFLOW_VERSION:-2.8.3}}",
    cpu=256,
    memory=512,
    environment=airflow_webserver_env,
    command=["webserver"],
)

flower_task_def_arn = create_task_definition(
    service_name="flower",
    image="${AIRFLOW_IMAGE_NAME:-parkpulse:${AIRFLOW_VERSION:-2.8.3}}",
    cpu=256,
    memory=512,
    environment=flower_env,
    command=["celery", "flower"],
)

scheduler_task_def_arn = create_task_definition(
    service_name="scheduler",
    image="${AIRFLOW_IMAGE_NAME:-parkpulse:${AIRFLOW_VERSION:-2.8.3}}",
    cpu=256,
    memory=512,
    environment=scheduler_env,
    command=["scheduler"],
)

worker_task_def_arn = create_task_definition(
    service_name="worker",
    image="${AIRFLOW_IMAGE_NAME:-parkpulse:${AIRFLOW_VERSION:-2.8.3}}",
    cpu=256,
    memory=512,
    environment=worker_env,
    command=["celery", "worker"],
)

# Print task definition ARNs
print("airflow-webserver Task Definition ARN:", airflow_webserver_task_def_arn)
print("flower Task Definition ARN:", flower_task_def_arn)
print("scheduler Task Definition ARN:", scheduler_task_def_arn)
print("worker Task Definition ARN:", worker_task_def_arn)
