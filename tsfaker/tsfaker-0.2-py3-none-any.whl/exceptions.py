class TsfakerException(Exception):
    pass


class TypeNotImplementedError(TsfakerException):
    pass


class DifferentNumberInputOutput(TsfakerException):
    def __init___(self, input_descriptors, output_files):
        super().__init__(self, 'The number of schema descriptors ({}) and output files paths ({}) '
                               'should be identical'.format(len(input_descriptors), len(output_files)))
