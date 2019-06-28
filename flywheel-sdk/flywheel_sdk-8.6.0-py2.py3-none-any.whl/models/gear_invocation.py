"""Provides gear invocation support"""
from .. import util

class GearInvocation(object):
    """Represents the details necessary to execute a gear as a job"""
    def __init__(self, gear):
        self.gear = gear

        # Setup default config
        self.config = gear.get_default_config()

        self.inputs = {}
        self.destination = None
        self.analysis_label = None
        self.tags = []

        self.__context = None

    def _set_context(self, context):
        self.__context = context

    def update_config(self, *args, **kwargs):
        """Update configuration values"""
        body = util.params_to_dict('update_config', args, kwargs)
        self.config.update(body)

    def set_analysis_label(self, label):
        """Set the analysis label, if executing an analysis gear"""
        if not self.gear.is_analysis_gear():
            raise ValueError('{} is not an analysis gear!'.format(self.gear.gear.name))
        self.analysis_label = label

    def add_tag(self, tag):
        """Add a tag to the job"""
        if tag not in self.tags:
            self.tags.append(tag)

    def add_tags(self, tags):
        """Add multiple tags to the job"""
        self.tags += tags

    def set_input(self, key, input):
        """Add an input"""
        self.inputs[key] = util.to_ref(input)

    def set_destination(self, dest):
        """Set the destination container"""
        self.destination = util.to_ref(dest)

    def run(self):
        """Run the invocation as a single job (or analysis).

        Requires that required inputs and the destination have been set.

        Returns the job id, or the analysis id in the case of an analysis gear.
        """
        from flywheel.models import Job
        job = Job(
            gear_id = self.gear.id,
            inputs = self.inputs,
            destination = self.destination,
            config = self.config,
            tags = self.tags
        )

        if self.gear.is_analysis_gear():
            # Create a new analysis object using label and job object
            return self._add_analysis(job)

        # Otherwise, just create the job
        return self.__context.add_job(job)

    def propose_batch(self, containers, optional_input_policy='ignored'):
        """Create a batch run proposal for the given containers

        :param list containers: The list of containers to run the job on
        :param str optional_input_policy: The optional input policy (default is ignored)
        """
        from flywheel.models import AnalysisInput, BatchProposalInput

        targets = [util.to_ref(input) for input in containers]

        if self.gear.is_analysis_gear():
            analysis_label = self.analysis_label or self._make_default_label()
            analysis = AnalysisInput(label=analysis_label)
        else:
            analysis = None

        proposal = BatchProposalInput(
            gear_id = self.gear.id,
            config = self.config,
            tags = self.tags,
            optional_input_policy = optional_input_policy,
            analysis=analysis,
            targets=targets
        )

        return self.__context.propose_batch(proposal)

    def _make_default_label(self):
        """Create a default label for an analysis run"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return '{} {}'.format(self.gear.gear.name, timestamp)

    def _add_analysis(self, job):
        """Add an analysis to the destination container"""
        from flywheel.models import AnalysisInput

        # Ensure a valid analysis label
        analysis_label = self.analysis_label or self._make_default_label()

        # Get destination type (from ref)
        dest_id = self.destination and self.destination.get('id')
        dest_type = self.destination and self.destination.get('type')
        if not dest_id or not dest_type:
            raise ValueError('Must specify a valid destination to create an analysis!')

        fname = 'add_{}_analysis'.format(dest_type)
        fn = getattr(self.__context, fname, None)
        if not fn:
            raise ValueError('{} is not a function!'.format(fname))

        # Ensure destination is unset
        job.destination = None
        return fn(dest_id, AnalysisInput(label=analysis_label, job=job))
