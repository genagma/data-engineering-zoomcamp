from prefect.infrastructure.docker import DockerContainer

# Alternative to creating DockerContainer block in the UI
docker_block = DockerContainer (
    image="antaresgendocker/prefect:dez", # insert your image here
    image_pull_policy="ALWAYS",
    auto_remove=True,
)

docker_block.save("dez-docker", overwrite=True)