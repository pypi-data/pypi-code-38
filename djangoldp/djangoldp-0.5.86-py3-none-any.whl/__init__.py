from django.db.models import options

__version__ = '0.5.86'
options.DEFAULT_NAMES += ('lookup_field', 'rdf_type', 'rdf_context', 'auto_author', 'view_set', 'container_path', 'permission_classes', 'serializer_fields', 'nested_fields', 'depth', 'many_depth')