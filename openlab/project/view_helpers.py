import requests
from os.path import dirname, basename

from django.shortcuts import render, get_object_or_404

from .models import Project


def get_project(request, project_path, action='edit'):
    project = get_object_or_404(Project, path=project_path)

    # Handle invisible projects, etc
    if action == 'edit':
        if not project.editable_by(request.user):
            raise Http403()

    return project


GITHUB_API = 'https://api.github.com/repos/michaelpb/omnithumb/git/trees/master?recursive=1'
def git_tree(git_url):
    r = requests.get(GITHUB_API)
    print(r.json())
    return r.json()['tree']

def git_tree_by_dir(git_url):
    tree = git_tree(git_url)

    files_by_dir = []
    for file_dict in tree:
        path = dirname(file_dict['path'])
        filename = basename(file_dict['path'])
        file_dict['title'] = filename
        file_dict['photo'] = {
            'preview_image_thumb': {
                'url': '',
            }
        }
        file_dict['path'] = {
            'url': file_dict['url'],
        }
        files_by_dir.append((
            path,
            file_dict,
        ))

    return files_by_dir
