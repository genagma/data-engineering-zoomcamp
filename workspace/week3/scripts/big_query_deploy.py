from prefect.deployments import Deployment
from etl_web_gcs_bq import etl_parent_flow
from prefect.filesystems import GitHub

github_storage = GitHub.load("dez-github")

deployment_github_storage = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name="big-query-flow",
    parameters={"month": "01", "year": 2019, "service": "fhv"},
    storage=github_storage,
    entrypoint="workspace/week3/scripts/etl_web_gcs_bq.py:etl_parent_flow",
)

deployment_github_storage.apply()