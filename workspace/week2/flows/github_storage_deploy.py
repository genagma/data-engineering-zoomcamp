from prefect.deployments import Deployment
from etl_web_to_gcs_github import etl_web_to_gcs_github
from prefect.filesystems import GitHub

github_storage = GitHub.load("dez-github")

deployment_github_storage = Deployment.build_from_flow(
    flow=etl_web_to_gcs_github,
    name="github-flow",
    storage=github_storage,
    entrypoint="workspace/week2/flows/etl_web_to_gcs_github.py:etl_web_to_gcs_github",
)

deployment_github_storage.apply()