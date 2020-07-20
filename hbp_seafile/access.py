from hbp_seafile.repos import Repos
from hbp_seafile.files import SeafFile

def get_file_by_url(client, file_url):
    """Get a single repo associated with specified repo_url
    Example inputs:
    1) https://drive.ebrains.eu/lib/0fee1620-062d-4643-865b-951de1eee355/file/sample-latest.csv
    2) https://drive.ebrains.eu/lib/0fee1620-062d-4643-865b-951de1eee355/file/Dir1/data.json
    """
    if "drive.ebrains.eu/lib/" in file_url:
        repo_id = file_url.split("drive.ebrains.eu/lib/")[1].split("/")[0]
        file_path = "/" + "/".join(file_url.split("drive.ebrains.eu/lib/")[1].split("/")[2:])
    else:
        raise ValueError("Parameter `file_url` does not have expected format!")

    repo_obj = Repos(client).get_repo(repo_id)
    file_obj = repo_obj.get_file(file_path)
    return file_obj
