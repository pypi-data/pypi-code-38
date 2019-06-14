import collections
import copy
import fnmatch
import fs
import os
import sys

from queue import Empty, LifoQueue

from ..util import set_nested_attr, sorted_container_nodes, METADATA_ALIASES, NO_FILE_CONTAINERS
from .abstract_importer import AbstractImporter
from .container_factory import ContainerFactory
from .template import CompositeNode, TERMINAL_NODE
from .packfile import PackfileDescriptor

IGNORED_FILE_LIST = [
    '.*',
    'ehthumbs.db',
    'Thumbs.db',
    'Icon\r'
]

class VisitTarget(object):
    """Represents a single node to visit while scanning"""
    def __init__(self, path, resolve, context, template_node):
        self.path = path
        self.resolve = resolve
        self.context = context
        self.template_node = template_node

def should_ignore_file(name):
    """Check if the given filename should be ignored"""
    for pattern in IGNORED_FILE_LIST:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False

class FolderImporter(AbstractImporter):
    def __init__(self, group=None, project=None,  repackage_archives=False,
            merge_subject_and_session=False, context=None, config=None):
        """Class that handles state for folder import.

        Arguments:
            group (str): The optional group id
            project (str): The optional project label or id in the format <id:xyz>
            repackage_archives (bool): Whether or not to repackage (and validate and de-identify) zipped packfiles. Default is False.
            merge_subject_and_session (bool): Whether or not subject or session layer is missing. Default is False.
            config (Config): The config object
        """
        super(FolderImporter, self).__init__(group, project, repackage_archives, context, config)

        self.root_node = None
        self._last_added_node = None
        self.merge_subject_and_session = merge_subject_and_session

    def add_template_node(self, next_node):
        """Append next_node to the last node that was added (or set the root node)

        Arguments:
            next_node (ImportTemplateNode): The node to append
        """
        last = self._last_added_node
        if last:
            if not hasattr(last, 'set_next'):
                raise ValueError('Cannot add node - invalid node type: {}'.format(type(last)))

            last.set_next(next_node)
        else:
            self.root_node = next_node

        self._last_added_node = next_node

    def add_composite_template_node(self, nodes):
        """Append a composite node to the last node that was added.

        Arguments:
            nodes (list): The list of nodes to append
        """
        composite = CompositeNode(nodes)
        self.add_template_node(composite)
        self._last_added_node = nodes[-1]

    def perform_discover(self, walker, context, queue=None, timeout=0):
        """Performs discovery of containers to create and files to upload in the given folder.

        Arguments:
            walker (obj): The walker instance
            follow_symlinks (bool): Whether or not to follow links (if supported by walker). Default is False.
            context (dict): The initial context
        """
        if queue is None:
            queue = LifoQueue()

        # Add initial item
        queue.put(VisitTarget('/', True, self.initial_context(), self.root_node))

        while True:
            try:
                if timeout:
                    target = queue.get(timeout=timeout)
                else:
                    target = queue.get(False)

                self.visit_dir(walker, queue, target)
                queue.task_done()
            except Empty:
                break  # Queue is empty, so stop

    def visit_dir(self, walker, queue, target):
        """Performs recursive discovery of containers to create and files to upload in the given folder.

        Arguments:
            walker (obj): The walker to query
            queue (Queue): The queue to add paths to
            target (VisitTarget): Queue entry being visited
        """
        context = target.context
        resolve = target.resolve

        # We only need to query for symlink if we're NOT following them
        for path, dirs, files in walker.walk(target.path, max_depth=1):

            for f in files:
                # Check if it's in the exclusion list
                if should_ignore_file(f.name):
                    continue

                packfile_desc = context.get('packfile_desc')
                if packfile_desc is not None:
                    packfile_desc.count += 1
                else:
                    child_path = walker.combine(target.path, f.name)
                    context.setdefault('files', []).append(child_path)

            for d in dirs:
                next_node = None
                child_path = walker.combine(target.path, d.name)

                if 'packfile' in context:
                    child_context = context
                else:
                    child_context = context.copy()
                    child_context.pop('files', None)

                    if target.template_node in (None, TERMINAL_NODE):
                        # Treat as packfile
                        child_context['packfile'] = d.name
                    else:
                        next_node = target.template_node.extract_metadata(d.name, child_context, walker, path=child_path)

                if not child_context.get('ignore', False):
                    # Set the packfile descriptor for file collection
                    packfile_type = child_context.get('packfile')
                    if packfile_type and 'packfile_desc' not in child_context:
                        packfile_name = child_context.get('packfile_name')
                        child_context['packfile_desc'] = PackfileDescriptor(packfile_type,
                            child_path, 0, name=packfile_name)

                    if next_node and next_node.node_type == 'scanner':
                        messages = next_node.scan(walker, child_path, child_context,
                            self.container_factory, self.audit_log)
                        self.messages += messages
                        resolve = False
                    else:
                        resolve_child = 'packfile' not in context
                        queue.put(VisitTarget(child_path, resolve_child, child_context, next_node))

        # Resolve the container
        if resolve:
            if self.merge_subject_and_session:
                self._context_merge_subject_and_session(context)

            container = self.container_factory.resolve(context)
            if container:
                files = context.get('files')
                packfile_desc = context.get('packfile_desc')

                if packfile_desc is not None:
                    container.packfiles.append(packfile_desc)
                elif files:
                    container.files.extend(files)
            else:
                self.messages.append(('warn', 'Ignoring files for folder {} because it represents an ambiguous node'.format(target.path)))

    def _context_merge_subject_and_session(self, context):
        """Merge session & subject labels"""
        merged = False
        if 'session' in context and 'label' in context['session']:
            context.setdefault('subject', {})['label'] = context['session']['label']
            merged = True
        if not merged and 'subject' in context and 'label' in context['subject']:
            context.setdefault('session', {})['label'] = context['subject']['label']
            merged = True
        return merged
