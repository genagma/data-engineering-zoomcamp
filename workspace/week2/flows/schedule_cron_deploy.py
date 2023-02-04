from etl_web_to_gcs import etl_web_to_gcs
from prefect.deployments import Deployment

deployment = Deployment.build_from_flow(
    flow=etl_web_to_gcs,
    name="scheduling-cron-deployment", 
    version=1, 
    work_queue_name="default",
    schedule={
        'cron': '0 5 1 * *',
        'timezone': 'UTC',
        'day_or': True
    },
)
deployment.apply()