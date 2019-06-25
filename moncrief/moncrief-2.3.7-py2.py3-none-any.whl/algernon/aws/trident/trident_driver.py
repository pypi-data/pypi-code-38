from algernon.aws.trident.connections import TridentNotary


class TridentDriver:
    def __init__(self, **kwargs):
        self._read_notary = kwargs.get('read_notary', TridentNotary.get_for_reader(**kwargs))
        self._write_notary = kwargs.get('write_notary', TridentNotary.get_for_writer(**kwargs))
        self._batch_mode = False

    def get(self, internal_id):
        command = "g.V('%s')" % internal_id
        return self.execute(command, True)

    def execute(self, query_text, read_only=False):
        if self._batch_mode is True:
            self._batch_commands.append(query_text)
            return
        notary = self._write_notary
        if read_only:
            notary = self._read_notary
        results = notary.send(query_text)
        return results

    def __enter__(self):
        self._batch_commands = []
        self._batch_mode = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type and not exc_val:
            self._batch_mode = False
            if self._batch_commands:
                commands = ';'.join(self._batch_commands)
                self.execute(commands)
            self._batch_commands = []
            return True
        raise (exc_type(exc_val))
