from tunga_projects.models import ProjectMeta
from tunga_utils.helpers import clean_meta_value


def save_project_metadata(project_id, meta_info):
    if isinstance(meta_info, dict):
        for meta_key in meta_info:
            ProjectMeta.objects.update_or_create(
                project_id=project_id, meta_key=meta_key, defaults=dict(meta_value=clean_meta_value(meta_info[meta_key]))
            )
