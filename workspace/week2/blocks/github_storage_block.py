from prefect.filesystems import GitHub

# alternative to creating GitHub block in the UI
gh_block = GitHub(
    name="dez-github", repository="https://github.com/genagma/data-engineering-zoomcamp"
)

gh_block.save("dez-github", overwrite=True)