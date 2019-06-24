class ActionRunProcessor(object):
    NAME = 'script'

    def __init__(self, configuration, processor_factory):
        self.processor = processor_factory.get_processor(configuration['operations'])

        if 'post_operations' in configuration:
            self.post_processor = processor_factory.get_processor(configuration['post_operations'])
        else:
            self.post_processor = None

    def execute(self, aug_id, namespace, output):
        self.processor.process(namespace)
        output.send_user_message(aug_id, namespace['store'])

        if self.post_processor:
            output.flush_messages()
            self.post_processor.process(namespace)
