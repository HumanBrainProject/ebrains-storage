from hbp_seafile.repo import Repo
from hbp_seafile.utils import raise_does_not_exist

class Repos(object):
    def __init__(self, client):
        self.client = client

    def create_repo(self, name, password=None):
        data = {'name': name}
        if password:
            data['passwd'] = password
        repo_json = self.client.post('/api2/repos/', data=data).json()
        return self.get_repo(repo_json['repo_id'])

    @raise_does_not_exist('The requested library does not exist')
    def get_repo(self, repo_id):
        """Get the repo which has the id `repo_id`.

        Raises :exc:`DoesNotExist` if no such repo exists.
        """
        repo_json = self.client.get('/api2/repos/' + repo_id).json()
        return Repo.from_json(self.client, repo_json)

    def list_repos(self):
        repos_json = self.client.get('/api2/repos/').json()
        return [Repo.from_json(self.client, j) for j in repos_json]

    def get_repos_by_filter(self, filter_name, filter_value):
        """Get all repos which have `filter_name` = `filter_value`.
        Note
        """
        repos_json = self.client.get('/api2/repos/').json()
        print
        match_repos = []
        for j in repos_json:
            if filter_name in j.keys() and j[filter_name] == filter_value:
                match_repos.append(Repo.from_json(self.client, j))
        return match_repos

    def get_repos_by_name(self, repo_name):
        """Get all repos which have the name `repo_name`.
        Note: can return multiple entries for same repo (same UUID) 
        """
        return self.get_repos_by_filter("name", repo_name)

    def get_repo_by_url(self, repo_url):
        """Get a single repo associated with specified repo_url
        Example inputs:
        1) https://wiki.ebrains.eu/bin/view/Collabs/shailesh-testing/
        2) wiki.ebrains.eu/bin/view/Collabs/shailesh-testing
        3) shailesh-testing

        Note: not guaranteed to identify as url and repo not easily linkable; url and name need not be same
        """
        if "wiki.ebrains.eu/bin/view/Collabs/" in repo_url:
            repo_path = repo_url.split("wiki.ebrains.eu/bin/view/Collabs/")[1]
        else:
            repo_path = repo_url
        repo_path = repo_path[:-1] if repo_path[-1] == "/" else repo_path 
        repo_owner = "collab-" + repo_path + "-administrator"

        match_repos = self.get_repos_by_filter("owner", repo_owner)
        
        if len(match_repos) == 0:
            raise Exception("Couldn't identify any repo associated with specified URL!")
        elif len(match_repos) > 1:
            raise Exception("Couldn't uniquely identify the repo associated with specified URL!")
        else:
            return match_repos[0]