from django.shortcuts import render, get_object_or_404

from .models import Project, FileModel


def get_project(request, project_path, action='edit'):
    project = get_object_or_404(Project, path=project_path)

    # Handle invisible projects, etc
    if action == 'edit':
        if not project.editable_by(request.user):
            raise Http403()

    return project

