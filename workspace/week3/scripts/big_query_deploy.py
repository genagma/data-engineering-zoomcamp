from prefect.deployments import Deployment
from etl_web_gcs_bq import el_parent_flow
from prefect.filesystems import GitHub

github_storage = GitHub.load("dez-github")

deployment_github_storage = Deployment.build_from_flow(
    flow=el_parent_flow,
    name="big-query-flow",
    storage=github_storage,
    entrypoint="workspace/week3/scripts/etl_web_gcs_bq.py:el_parent_flow",
)

deployment_github_storage.apply()