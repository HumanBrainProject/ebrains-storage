ebrains_drive
==============

Python client interface for HBP Collaboratory Seafile storage


Original implementation source:
https://github.com/haiwen/python-seafile
by Shuai Lin (linshuai2012@gmail.com)


Updated for integration with HBP v2 Collaboratory's Seafile storage
by Shailesh Appukuttan (appukuttan.shailesh@gmail.com)


Documentation: https://github.com/HumanBrainProject/ebrains-drive/blob/master/doc.md

Installation: `pip install ebrains_drive`


Example usage (refer to docs for more):

```python
    # 1. Import module
    import ebrains_drive

    # 2. Create client object
    # 2.1 either via
    client = ebrains_drive.connect('hbp_username', 'password')
    # 2.2 or via
    from ebrains_drive.client import DriveApiClient
    client = DriveApiClient(username="hbp_username", password="password")

    
    # 3. Working with Collab drives (libraries / repos)
    # 3.1 Get list of all libraries that user has access to
    list_repos =  client.repos.list_repos()
    # 3.2 Get info of specific library
    repo_obj = client.repos.get_repo('0fee1620-062d-4643-865b-951de1eee355')
    print(repo_obj.__dict__)

    # 4. Working with directories
    # 4.1 Get info of a directory 
    repo_obj = client.repos.get_repo('0fee1620-062d-4643-865b-951de1eee355')
    dir_obj = repo_obj.get_dir('/') # specify dir path; '/' signifies root directory
    print(dir_obj.__dict__)
    # 4.2 Get contents of directory
    dir_obj.ls()


    # 5. Working with files
    # 5.1 Get info of a file 
    repo_obj = client.repos.get_repo('0fee1620-062d-4643-865b-951de1eee355')
    file_obj = repo_obj.get_file('/sample-latest.csv') # specify file path
    print(file_obj.__dict__)
    # 5.2 Get file content
    file_content = file_obj.get_content()
    print(file_content)
```


<div><img src="https://raw.githubusercontent.com/HumanBrainProject/ebrains-drive/master/eu_logo.jpg" alt="EU Logo" width="15%" align="right"></div>

### ACKNOWLEDGEMENTS
This open source software code was developed in part in the Human Brain Project, funded from the European Union's Horizon 2020 Framework Programme for Research and Innovation under Specific Grant Agreements No. 720270 and No. 785907 (Human Brain Project SGA1 and SGA2).