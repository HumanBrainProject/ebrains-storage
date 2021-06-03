import os.path
import re

from ebrains_drive.repos import Repos
from ebrains_drive.files import SeafFile


class File(object):
    def __init__(self, client):
        self.client = client

    def get_file_by_url(self, file_url):
        """Get a single repo associated with specified repo_url
        Example inputs:
        1) https://drive.ebrains.eu/lib/0fee1620-062d-4643-865b-951de1eee355/file/sample-latest.csv
        2) https://drive.ebrains.eu/lib/0fee1620-062d-4643-865b-951de1eee355/file/Dir1/data.json
        """

        regex = r".*\/lib\/(.*)\/file(\/.*)"

        matches = re.search(regex, file_url)
        if matches is None:
            raise ValueError("Parameter `file_url` does not have expected format!")
        else:
            repo_id = matches.group(1)
            file_path = matches.group(2)

        repo_obj = self.client.repos.get_repo(repo_id)
        file_obj = repo_obj.get_file(file_path)
        return file_obj

    def get_file_by_local_path(self, local_path):
        """
        Get the file or directory object corresponding to `local_path`
        when the Drive is mounted in the EBRAINS Lab.
        """
        home_dir = "/mnt/user/drive/My Libraries/My Library/"
        group_dir = "/mnt/user/drive/Shared with groups/"
        shared_dir = "/mnt/user/shared/"
        if local_path.startswith(home_dir):
            repo_obj = self.client.repos.get_default_repo()
            relative_path = os.path.relpath(local_path, home_dir)
        elif local_path.startswith(group_dir):
            collab_name = local_path.split("/")[5]
            repo_obj = self.client.repos.get_repos_by_name(collab_name)
            relative_path = os.path.relpath(local_path, f"{group_dir}{collab_name}/")
        elif local_path.startswith(shared_dir):
            collab_name = local_path.split("/")[4]
            repo_obj = self.client.repos.get_repos_by_name(collab_name)
            relative_path = os.path.relpath(local_path, f"{shared_dir}{collab_name}/")
        else:
            raise Exception("Couldn't identify any file associated with specified path.")
        if len(repo_obj) == 0:
            raise Exception("Couldn't identify any file associated with specified path.")
        elif len(repo_obj) > 1:
            raise Exception("Couldn't uniquely identify the repo associated with specified path.")
        else:
            return repo_obj[0].get_file("/" + relative_path)
