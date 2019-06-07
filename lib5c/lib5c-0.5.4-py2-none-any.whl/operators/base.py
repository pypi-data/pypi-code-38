from copy import deepcopy, copy

from lib5c.core.interactions import InteractionMatrix


class InteractionMatrixOperator(object):
    """
    Abstract base class for objects that operate on single InteractionMatrix
    objects.

    Subclasses should implement an ``apply_inplace()`` function that takes in an
    InteractionMatrix object and returns an InteractionMatrix object but is
    allowed to operate in-place. Additional parameters requried by the
    ``apply_inplace()`` function can be either passed to the function as
    ``**kwargs`` or stored in properties of the InteractionMatrixOperator
    subclass.
    """

    def apply(self, target, **kwargs):
        """
        Apply this operator to a target InteractionMatrix, returning a copy.

        Parameters
        ----------
        target : InteractionMatrix
            The InteractionMatrix object to operate on.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        InteractionMatrix
            The result of applying the operation.
        """
        return self.apply_inplace(deepcopy(target), **kwargs)

    def apply_inplace(self, target, **kwargs):
        """
        Apply this operator to a target InteractionMatrix in-place.

        Parameters
        ----------
        target : InteractionMatrix
            The InteractionMatrix object to operate on.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        InteractionMatrix
            The result of applying the operation.
        """
        raise NotImplementedError("InteractionMatrixOperator subclasses should"
                                  "implement an apply_inplace() function.")

    def apply_by_region(self, target, **kwargs):
        """
        Apply this operator independently to each region of a target
        InteractionMatrix.

        Parameters
        ----------
        target : InteractionMatrix
            The InteractionMatrix object to operate on.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        InteractionMatrix
            The result of applying the operation.

        Notes
        -----
        To support logging, we used the following pattern:

            1. Log on the target object to indicate regional application
            2. Maintain a list of results of the application
            3. Instantiate
            4. Get the first result from the list and copy its log to the
               instance
            5. Log on the result object to indicate end of regional application
            6. Return the instance

        If you see ``'applying by region'`` with no closing ``'done applying by
        region'``, that indictates that you are looking at a target object for
        an apply-by-region operation that was not done in-place. Such a log line
        can be ignored.

        If you see ``'applying by region'`` with a closing ``'done applying by
        region'``, that indicates that you are looking at a result object for
        an apply-by-region operation that was not done in-place. The lines in
        the block show the log for only the first region, but each region was
        processed identically.
        """
        target.log_event('applying by region')
        im_list = [self.apply(target[region], **kwargs)
                   for region in target.get_regions()]
        inst = InteractionMatrix.from_list(im_list)
        inst.log = copy(im_list[0].log)
        inst.log_event('done applying by region')
        return inst


class MultiInteractionMatrixOperator(object):
    """
    Abstract base class for objects that operate on multiple InteractionMatrix
    objects.

    Subclasses should implement an ``apply_inplace()`` function that takes in an
    list of InteractionMatrix objects and returns a list of InteractionMatrix
    objects but is allowed to operate in-place. Additional parameters requried
    by the ``apply_inplace()`` function can be either passed to the function as
    ``**kwargs`` or stored in properties of the MultiInteractionMatrixOperator
    subclass.
    """

    def apply(self, targets, **kwargs):
        """
        Apply this operator to a list of target InteractionMatrix objects.

        Parameters
        ----------
        targets : list of InteractionMatrix
            The list of InteractionMatrix objects to operate on simultaneously.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        list of InteractionMatrix
            The result of applying the operation.
        """
        return self.apply_inplace(deepcopy(targets), **kwargs)

    def apply_inplace(self, targets, **kwargs):
        """
        Apply this operator to a target InteractionMatrix in-place.

        Parameters
        ----------
        targets : list of InteractionMatrix
            The list of InteractionMatrix objects to operate on simultaneously.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        list of InteractionMatrix
            The result of applying the operation.
        """
        raise NotImplementedError("InteractionMatrixOperator subclasses should"
                                  "implement an apply_inplace() function.")

    def apply_by_region(self, targets, **kwargs):
        """
        Apply this operator independently to each region of the target
        InteractionMatrix objects.

        Parameters
        ----------
        targets : list of InteractionMatrix
            The list of InteractionMatrix objects to operate on simultaneously.
        kwargs : other keyword arguments
            To be utilized by subclasses.

        Returns
        -------
        list of InteractionMatrix
            The result of applying the operation.

        Notes
        -----
        To support logging, we used the following pattern:

            1. Log on all target objects to indicate regional application
            2. Maintain a dict of list of results of the application
            3. Instantiate the results
            4. Get the first region of the first result from the dict of lists
               and copy its log to each instance
            5. Log on all result objects to indicate end of regional application
            6. Return the instances

        If you see ``'applying by region'`` with no closing ``'done applying by
        region'``, that indictates that you are looking at a target object for
        an apply-by-region operation that was not done in-place. Such a log line
        can be ignored.

        If you see ``'applying by region'`` with a closing ``'done applying by
        region'``, that indicates that you are looking at a result object for
        an apply-by-region operation that was not done in-place. The lines in
        the block show the log for only the first region, but each region was
        processed identically.
        """
        for target in targets:
            target.log_event('applying by region')
        regions = targets[0].get_regions()
        results_by_region = {region: self.apply([target[region]
                                                 for target in targets],
                                                **kwargs)
                             for region in regions}
        results = [InteractionMatrix.from_list([results_by_region[region][i]
                                                for region in regions])
                   for i in range(len(targets))]
        for result in results:
            result.log = copy(results_by_region[regions[0]][0].log)
            result.log_event('done applying by region')
        return results
