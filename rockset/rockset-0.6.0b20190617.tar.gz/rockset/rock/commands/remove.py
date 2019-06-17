from .command_auth import AuthCommand
from .util.parse_util import parse_collection_path

class Remove(AuthCommand):
    def usage(self):
        return """
usage: rock rm [-h] <name> <document_id>...

Remove one or more documents from a Rockset collection.

arguments:
    <name>              name of the collection
    <document_id>       id of the documents you wish to remove from the
                        collection

options:
    -h, --help          show this help message and exit
        """

    def go(self):
        workspace, name = parse_collection_path(self.name)
        resource = self.client.retrieve(name, workspace=workspace)
        docs = [{'_id': docid} for docid in self.document_id]
        self.print_list(
            0,
            resource.remove_docs(docs=docs),
            field_order=['collection', 'id', 'status', 'error']
        )
        return 0
