from .. import util
from ..finder import Finder
from .gear_mixin import GearMixin

class ContextBase(object):
    def __init__(self):
        self._context = None

    def _set_context(self, context):
        """Set the context object (i.e. flywheel client instance)"""
        self._context = context

class ContainerBase(object):
    def __init__(self):
        self.__context = None

    def _set_context(self, context):
        """Set the context object (i.e. flywheel client instance)"""
        self.__context = context
        self._update_files_parent(getattr(self, '_files', None))

    def _update_files_parent(self, files):
        # Set the parent for each file
        if files:
            for file_entry in files:
                file_entry._parent = self

    def _invoke_container_api(self, fmt, *args, **kwargs):
        """Invoke container api, formatting the string first"""
        if self.__context:
            fname = fmt.format(self.container_type)
            fn = getattr(self.__context, fname, None)
            if fn:
                return fn(*args, **kwargs)
        return None

    def _invoke_file_api(self, fmt, *args, **kwargs):
        """Invoke container api, formatting the string first"""
        if self.__context:
            fname = fmt.format(self.container_type)
            file_group = getattr(self, '_file_group', None)
            if file_group is not None:
                fname = fname.replace('file', file_group)
            fn = getattr(self.__context, fname, None)
            if fn:
                return fn(*args, **kwargs)
        return None

    def _add_child(self, child_type, args, kwargs):
        """Add a child to this container, returns the child that was created"""
        fname = 'add_{}'.format(child_type)

        body = util.params_to_dict(fname, args, kwargs)
        body[self.container_type] = self.id

        child_id = self._invoke_container_api(fname, body)
        if child_id:
            get_fname = 'get_{}'.format(child_type)
            return self._invoke_container_api(get_fname, child_id)

        return None

    def update(self, *args, **kwargs):
        """Update container using dictionary or kwargs"""
        # Could either pass a dictionary or kwargs values
        body = util.params_to_dict('update', args, kwargs)

        # Update the container
        return self._invoke_container_api('modify_{}', self.id, body)

    def reload(self):
        """Reload the object from the server, and return the result"""
        return self._invoke_container_api('get_{}', self.id)

    def ref(self):
        """Make a container reference"""
        return { 'type': self.container_type, 'id': self.id }

    def _localize_date(self, name):
        """Localize the date attribute for name"""
        value = getattr(self, name, None)
        if not value:
            return None
        from dateutil.tz import tzlocal
        return value.astimezone(tzlocal())

    @property
    def local_created(self):
        """Get the creation time in the local timezone"""
        return self._localize_date('created')

    @property
    def local_modified(self):
        """Get the modification time in the local timezone"""
        return self._localize_date('modified')

    def _find_children(self, child_type, filters, find_first=False, find_one=False, **kwargs):
        fname = 'get_{}_{}'.format(self.container_type, child_type)
        return self.__context._find(fname, [self.id], filters, find_first=find_first, find_one=find_one, **kwargs)

    def __getattr__(self, name):
        # Return finders for children
        if name in self.child_types and self.id is not None:
            prop_name = '_{}'.format(name)
            result = getattr(self, prop_name, None)
            if result is None:
                # e.g. get_project_sessions
                fname = 'get_{}_{}'.format(self.container_type, name)
                result = Finder(self.__context, fname, self.id)
                setattr(self, prop_name, result)
            return result

        return getattr(object, name)

class InfoMethods(object):
    def replace_info(self, info):
        """Fully replace this object's info with the provided value"""
        return self._invoke_container_api('replace_{}_info', self.id, info)

    def update_info(self, *args, **kwargs):
        """Update the info with the passed in arguments"""
        # Could either pass a dictionary or kwargs values
        body = util.params_to_dict('update_info', args, kwargs)
        return self._invoke_container_api('set_{}_info', self.id, body)

    def delete_info(self, *args):
        """Delete the info fields listed in args"""
        body = util.params_to_list(args)
        return self._invoke_container_api('delete_{}_info_fields', self.id, body)


class TagMethods(object):
    def add_tag(self, tag):
        """Add the given tag to the object"""
        return self._invoke_container_api('add_{}_tag', self.id, tag)

    def rename_tag(self, tag, new_tag):
        """Rename tag on object"""
        return self._invoke_container_api('rename_{}_tag', self.id, tag, new_tag)

    def delete_tag(self, tag):
        """Delete tag from object"""
        return self._invoke_container_api('delete_{}_tag', self.id, tag)


class NoteMethods(object):
    def add_note(self, message):
        """Add the given note to the object"""
        return self._invoke_container_api('add_{}_note', self.id, message)

    def delete_note(self, note_id):
        """Delete the given note on the object"""
        return self._invoke_container_api('delete_{}_note', self.id, note_id)


class PermissionMethods(object):
    def add_permission(self, permission):
        """Add a permission to a container"""
        return self._invoke_container_api('add_{}_permission', self.id, permission)

    def update_permission(self, user_id, permission):
        """Update a user's permission on container"""
        return self._invoke_container_api('modify_{}_user_permission', self.id, user_id, permission)

    def delete_permission(self, user_id):
        """Delete a user's permission from container"""
        return self._invoke_container_api('delete_{}_user_permission', self.id, user_id)


class DownloadMethods(object):
    def download_tar(self, dest_file, include_types=None, exclude_types=None):
        """Download the container as a tarball to dest_file.

        :param str dest_file: (required) The destination file on disk
        :param list include_types: The optional list of types to include in the download (e.g. ['nifti'])
        :param list exclude_types: The optional list of types to exclude from the download (e.g. ['dicom'])
        :return: A summary of the download
        """
        return self._invoke_container_api('download_tar', self, dest_file, include_types=include_types,
            exclude_types=exclude_types)


class AnalysisMethods(object):
    def add_analysis(self, *args, **kwargs):
        """Add an analysis to this container"""
        fname = 'add_{}_analysis'

        body = util.params_to_dict(fname, args, kwargs)
        analysis_id = self._invoke_container_api(fname, self.id, body)

        if analysis_id:
            return self._invoke_container_api('get_analysis', analysis_id)

        return None


class FileMethods(object):
    def upload_file(self, file):
        """Upload a file to a container"""
        return self._invoke_file_api('upload_file_to_{}', self.id, file)

    def download_file(self, file_name, dest_file):
        """Download file to the given path"""
        return self._invoke_file_api('download_file_from_{}', self.id, file_name, dest_file)

    def get_file_download_url(self, file_name):
        """Get a ticketed download url for the file"""
        return self._invoke_file_api('get_{}_download_url', self.id, file_name)

    def read_file(self, file_name):
        """Read the contents of the file"""
        return self._invoke_file_api('download_file_from_{}_as_data', self.id, file_name)

    def update_file(self, file_name, *args, **kwargs):
        """Update a file's type and/or modality"""
        body = util.params_to_dict('update_file', args, kwargs)
        return self._invoke_file_api('modify_{}_file', self.id, file_name, body)

    def delete_file(self, file_name):
        """Delete file from the container"""
        return self._invoke_file_api('delete_{}_file', self.id, file_name)

    def replace_file_info(self, file_name, info):
        """Fully replace this file's info with the provided value"""
        return self._invoke_file_api('replace_{}_file_info', self.id, file_name, info)

    def update_file_info(self, file_name, *args, **kwargs):
        """Update the file's info with the passed in arguments"""
        # Could either pass a dictionary or kwargs values
        body = util.params_to_dict('update_file_info', args, kwargs)
        return self._invoke_file_api('set_{}_file_info', self.id, file_name, body)

    def delete_file_info(self, file_name, *args):
        """Delete the file info fields listed in args"""
        body = util.params_to_list(args)
        return self._invoke_file_api('delete_{}_file_info_fields', self.id, file_name, body)

    def replace_file_classification(self, file_name, classification, modality=None):
        """Fully replace a file's modality and classification"""
        body = {'replace': classification}
        if modality is not None:
            body['modality'] = modality
        return self._invoke_file_api('modify_{}_file_classification', self.id, file_name, body)

    def update_file_classification(self, file_name, classification):
        """Update a file's classification"""
        return self._invoke_file_api('set_{}_file_classification', self.id, file_name, classification)

    def delete_file_classification(self, file_name, classification):
        """Delete a file's classification fields"""
        return self._invoke_file_api('delete_{}_file_classification_fields', self.id, file_name, classification)

    def get_files(self):
        """Get the files collection, retrieving the container if necessary"""
        result = getattr(self, '_files', None)

        if result is None:
            obj = self._invoke_container_api('get_{}', self.id)
            result = getattr(obj, '_files', None)
            self._update_files_parent(result)

        return result

    def get_file(self, name):
        """Get the first file entry with the given name, retrieving the container if necessary"""
        for entry in self.get_files():
            if entry.name == name:
                return entry
        return None

    def file_ref(self, name):
        """Get a reference to the given file"""
        entry = self.get_file()
        return entry.ref() if entry else None

    def get_file_zip_info(self, file_name):
        """Get zip member information for this file"""
        return self._invoke_file_api('get_{}_file_zip_info', self.id, file_name)

    def download_file_zip_member(self, file_name, member_path, dest_file):
        """Download file's zip member to the given path"""
        return self._invoke_file_api('download_file_from_{}', self.id, file_name, dest_file, member=member_path)

    def read_file_zip_member(self, file_name, member_path):
        """Read contents of file's zip member"""
        return self._invoke_file_api('download_file_from_{}_as_data', self.id, file_name, member=member_path)


class TimestampMethods(object):
    @property
    def local_timestamp(self):
        """Get the timestamp in the local timezone"""
        return self._localize_date('timestamp')

    @property
    def original_timestamp(self):
        """Get the timestamp in the original timezone"""
        if not self.timestamp:
            return None

        if not self.timezone:
            raise ValueError('No original timezone was specified!')

        import pytz
        tz = pytz.timezone(self.timezone)
        return self.timestamp.astimezone(tz)


class GroupMixin(ContainerBase, TagMethods, PermissionMethods):
    container_type = 'group'
    child_types = ['projects']

    def add_project(self, *args, **kwargs):
        """Add a project to this group"""
        return self._add_child('project', args, kwargs)


class ProjectMixin(ContainerBase, TagMethods, NoteMethods, PermissionMethods, FileMethods, InfoMethods,
                   DownloadMethods, AnalysisMethods):
    container_type = 'project'
    child_types = ['subjects', 'sessions', 'analyses', 'files']

    def add_subject(self, *args, **kwargs):
        """Add a subject to this project"""
        return self._add_child('subject', args, kwargs)

    def add_session(self, *args, **kwargs):
        """Add a session to this project"""
        return self._add_child('session', args, kwargs)


class SubjectMixin(ContainerBase, TagMethods, NoteMethods, FileMethods, InfoMethods, AnalysisMethods):
    container_type = 'subject'
    child_types = ['sessions', 'analyses', 'files']

    def add_session(self, *args, **kwargs):
        """Add a session to this subject"""
        fname = 'add_session'

        body = util.params_to_dict(fname, args, kwargs)

        # Adding a session requires project and subject id
        body['project'] = self.project
        body.setdefault('subject', {})
        body['subject']['_id'] = self.id

        session_id = self._invoke_container_api(fname, body)
        if session_id:
            return self._invoke_container_api('get_session', session_id)
        return None


class SessionMixin(ContainerBase, TagMethods, NoteMethods, FileMethods, InfoMethods, TimestampMethods,
                   DownloadMethods, AnalysisMethods):
    container_type = 'session'
    child_types = ['acquisitions', 'analyses', 'files']

    def add_acquisition(self, *args, **kwargs):
        """Add a acquisition to this session"""
        return self._add_child('acquisition', args, kwargs)

    @property
    def age_years(self):
        if self.age:
            return util.seconds_to_years(self.age)
        return self.age

    @property
    def age_months(self):
        if self.age:
            return util.seconds_to_months(self.age)
        return self.age

    @property
    def age_weeks(self):
        if self.age:
            return util.seconds_to_weeks(self.age)
        return self.age

    @property
    def age_days(self):
        if self.age:
            return util.seconds_to_days(self.age)
        return self.age


class AcquisitionMixin(ContainerBase, NoteMethods, TagMethods, FileMethods, InfoMethods, TimestampMethods,
                       DownloadMethods, AnalysisMethods):
    container_type = 'acquisition'
    child_types = ['analyses', 'files']


class AnalysisMixin(ContainerBase, NoteMethods, TagMethods, FileMethods, InfoMethods, DownloadMethods):
    container_type = 'analysis'
    child_types = ['files']
    _file_group = 'output'

    def upload_file(self, file):
        """Upload an output file to analysis"""
        return self._invoke_container_api('upload_output_to_analysis', self.id, file)

    def upload_output(self, file):
        """Upload an output file to analysis"""
        return self._invoke_container_api('upload_output_to_analysis', self.id, file)


class CollectionMixin(ContainerBase, NoteMethods, TagMethods, FileMethods, InfoMethods):
    container_type = 'collection'
    child_types = ['sessions', 'acquisitions', 'analyses', 'files']

    def add_sessions(self, *args, **kwargs):
        session_ids = []
        for arg in args:
            if isinstance(arg, str):
                session_ids.append(arg)
            else:
                session_ids.append(arg.id)

        return self._invoke_container_api('add_sessions_to_{}', self.id, session_ids, **kwargs)

    def add_acquisitions(self, *args, **kwargs):
        acquisition_ids = []
        for arg in args:
            if isinstance(arg, str):
                acquisition_ids.append(arg)
            else:
                acquisition_ids.append(arg.id)

        return self._invoke_container_api('add_acquisitions_to_{}', self.id, acquisition_ids, **kwargs)


class FileMixin(ContainerBase):
    container_type = 'file'
    child_types = []

    def __init__(self):
        super(FileMixin, self).__init__()
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @property
    def local_replaced(self):
        """Get the replaced timestamp in local time"""
        return self._localize_date('replaced')

    def url(self):
        """Get a ticketed download url for the file"""
        return self._parent.get_file_download_url(self.name)

    def download(self, dest_file):
        """Download file to the given path"""
        return self._parent.download_file(self.name, dest_file)

    def read(self):
        """Read the contents of the file"""
        return self._parent.read_file(self.name)

    def replace_info(self, info):
        """Fully replace this file's info with the provided value"""
        return self._parent.replace_file_info(self.name, info)

    def update_info(self, *args, **kwargs):
        """Update the file's info with the passed in arguments"""
        return self._parent.update_file_info(self.name, *args, **kwargs)

    def delete_info(self, *args):
        """Delete the file info fields listed in args"""
        return self._parent.delete_file_info(self.name, *args)

    def update(self, *args, **kwargs):
        """Update a file's type and/or modality"""
        return self._parent.update_file(self.name, *args, **kwargs)

    def replace_classification(self, classification, modality=None):
        """Fully replace a file's modality and classification"""
        return self._parent.replace_file_classification(self.name, classification, modality=modality)

    def update_classification(self, classification):
        """Update a file's classification"""
        return self._parent.update_file_classification(self.name, classification)

    def delete_classification(self, classification):
        """Delete a file's classification fields"""
        return self._parent.delete_file_classification(self.name, classification)

    def ref(self):
        """Make a file reference"""
        ref = self._parent.ref()
        ref['name'] = self.name
        return ref

    def get_zip_info(self):
        """Get zip member information for this file"""
        return self._parent.get_file_zip_info(self.name)

    def download_zip_member(self, member_path, dest_file):
        """Download file's zip member to the given path"""
        return self._parent.download_file_zip_member(self.name, member_path, dest_file)

    def read_zip_member(self, member_path):
        """Read contents of file's zip member"""
        return self._parent.read_file_zip_member(self.name, member_path)


class JobMixin(ContainerBase):
    container_type = 'job'
    child_types = []

    def change_state(self, new_state):
        """Change the state of the job to new_state"""
        return self._invoke_container_api('change_job_state', self.id, new_state)

    def get_logs(self):
        """Get the job log entries"""
        response = self._invoke_container_api('get_job_logs', self.id)
        return response.logs

    def print_logs(self, file=None):
        """Print logs to file (or stdout, if file is not specified)"""
        if file is None:
            import sys
            file = sys.stdout

        for item in self.get_logs():
            file.write(item.msg)

        file.flush()


class ResolverOutputMixin(object):
    def _set_context(self, context):
        """Set context and parent for files"""
        parent = None

        if self.path:
            for node in self.path:
                if getattr(node, 'container_type', None) == 'file':
                    node._parent = parent

                if hasattr(node, '_set_context'):
                    node._set_context(context)

                parent = node

        if self.children:
            for node in self.children:
                if hasattr(node, '_set_context'):
                    node._set_context(context)

            if getattr(node, 'container_type', None) == 'file':
                node._parent = parent


class SearchResponseMixin(object):
    def _set_context(self, context):
        if self.group is not None:
            self.group._set_context(context)

        if self.project is not None:
            self.project._set_context(context)

        if self.subject is not None:
            self.subject._set_context(context)

        if self.session is not None:
            self.session._set_context(context)

        if self.acquisition is not None:
            self.acquisition._set_context(context)

        if self.collection is not None:
            self.collection._set_context(context)

        if self.analysis is not None:
            self.analysis._set_context(context)

        if self.file is not None:
            # Set parent object on file
            self.file._parent = self.parent


class BatchProposalMixin(ContextBase):
    """Batch mixin that provides run/cancel shorthand"""
    def run(self):
        """Execute the batch proposal"""
        return self._context.start_batch(self.id)


class BatchMixin(ContextBase):
    """Batch mixin that provides cancel shorthand"""
    def cancel(self):
        """Cancel the batch proposal and any associated jobs"""
        return self._context.cancel_batch(self.id)
