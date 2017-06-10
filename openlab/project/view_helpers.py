import re
import requests

from collections import defaultdict
from urllib.parse import urlparse
from os.path import dirname, basename

from django.shortcuts import render, get_object_or_404

from .models import Project

# XXX
from .testing_data import HIVE_BARCELONA_WARRE 

nested_dict = lambda: defaultdict(nested_dict)
CHARS = re.compile(r'[\W_-]+')
def beautify_repo_name(value):
    return CHARS.sub(' ', value).strip().capitalize()

def get_project(request, project_path, action='edit'):
    project = get_object_or_404(Project, path=project_path)

    # Handle invisible projects, etc
    if action == 'edit':
        if not project.editable_by(request.user):
            raise Http403()

    return project


GITHUB_API = 'https://api.github.com/repos/michaelpb/omnithumb/git/trees/master?recursive=1'
def git_tree(git_url):
    return HIVE_BARCELONA_WARRE['tree']

def github_get_repo_commits(username, reponame):
    '''
    Gets API
    '''
    API = 'https://api.github.com/repos/%s/%s'
    url = API % (username, reponame)
    return requests.get(url).json()

def unflatten_tree(path, lst):
    leaves = [item for item in lst if item['dirname'] == path]
    nonleaves = [item for item in lst if item['dirname'] != path]
    subfiles = [item for item in nonleaves if item['dirname'].startswith(path)]
    subdirnames = set(
        item['path'][len(path):].split('/')[0]
        for item in subfiles
    )
    dirs = []
    for dirname in subdirnames:
        if path:
            full_path = '/'.join([path, dirname])
        else:
            full_path = dirname
        dirs.append({
            "basename": dirname,
            "type": "tree",
            "contents": unflatten_tree(full_path, lst),
        })
    return dirs + leaves

def git_tree_by_dir(git_url):
    tree = HIVE_BARCELONA_WARRE['tree']
    basenames = set()
    files = [item for item in tree if item['type'] == 'blob']
    for item in files:
        item['basename'] = basename(item['path'])
        item['dirname'] = dirname(item['path'])
        basenames.add(item['basename'])

    return unflatten_tree('', files)
