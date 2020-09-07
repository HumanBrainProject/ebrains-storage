from ebrains_drive.repos import Repos
from ebrains_drive.files import SeafFile

import re

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
        