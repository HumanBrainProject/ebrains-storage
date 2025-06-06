from urllib.parse import urlencode
from ebrains_drive.files import SeafDir, SeafFile
from ebrains_drive.utils import raise_does_not_exist


class Repo(object):
    """
    A seafile library
    """

    def __init__(self, client, **kwargs):
        self.client = client

        allowed_keys = [
            "encrypted",
            "group_name",
            "groupid",
            "head_commit_id",
            "id",
            "modifier_contact_email",
            "modifier_email",
            "modifier_name",
            "mtime",
            "mtime_relative",
            "name",
            "owner",
            "owner_contact_email",
            "owner_name",
            "permission",
            "root",
            "share_from",
            "share_from_contact_email",
            "share_from_name",
            "share_type",
            "size",
            "size_formatted",
            "type",
            "version",
            "virtual",
        ]
        # Update __dict__ but only for keys that have been predefined
        # (silently ignore others)
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)
        # To NOT silently ignore rejected keys
        # rejected_keys = set(kwargs.keys()) - set(allowed_keys)
        # if rejected_keys:
        #     raise ValueError("Invalid arguments in constructor:{}".format(rejected_keys))

    def __str__(self):
        return "(id='{}', name='{}')".format(self.id, self.name)

    def __repr__(self):
        return "ebrains_drive.repo.Repo(id='{}', name='{}')".format(self.id, self.name)

    @classmethod
    def from_json(cls, client, repo_json):
        return cls(client, **repo_json)

    def is_readonly(self):
        return "w" not in self.perm

    @raise_does_not_exist("The requested file does not exist")
    def get_file(self, path):
        """Get the file object located in `path` in this repo.

        Return a :class:`SeafFile` object
        """
        assert path.startswith("/")
        url = "/api2/repos/%s/file/detail/" % self.id
        query = "?" + urlencode(dict(p=path))
        file_json = self.client.get(url + query).json()

        return SeafFile(self, path, file_json["id"], "file", file_json["size"])

    @raise_does_not_exist("The requested dir does not exist")
    def get_dir(self, path):
        """Get the dir object located in `path` in this repo.

        Return a :class:`SeafDir` object
        """
        assert path.startswith("/")
        url = "/api2/repos/%s/dir/" % self.id
        query = "?" + urlencode(dict(p=path))
        resp = self.client.get(url + query)
        dir_id = resp.headers["oid"]
        dir_json = resp.json()
        dir = SeafDir(self, path, dir_id, "dir")
        dir.load_entries(dir_json)
        return dir

    def delete(self):
        """Remove this repo. Only the repo owner can do this"""
        self.client.delete("/api2/repos/" + self.id)

    def list_history(self):
        """List the history of this repo

        Returns a list of :class:`RepoRevision` object.
        """
        pass

    ## Operations only the repo owner can do:

    def update(self, name=None):
        """Update the name of this repo. Only the repo owner can do
        this.
        """
        pass

    def get_settings(self):
        """Get the settings of this repo. Returns a dict containing the following
        keys:

        `history_limit`: How many days of repo history to keep.
        """
        pass

    def restore(self, commit_id):
        pass


class RepoRevision(object):
    def __init__(self, client, repo, commit_id):
        self.client = client
        self.repo = repo
        self.commit_id = commit_id

    def restore(self):
        """Restore the repo to this revision"""
        self.repo.revert(self.commit_id)
