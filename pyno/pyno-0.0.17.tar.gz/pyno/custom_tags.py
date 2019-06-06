from pyno.tree_model import HTML as H
import warnings

# Create a special element for CDATA insertion
class CDATA(H):
    def construct(self, content, *args, **kwargs):
        return f"<![CDATA[{content}]]>"


# Create a special element that works for including different asset types. eg. javascript and stylesheets and icon
class Require(H):
    def construct(self, file_path, *args, **kwargs):
        if file_path.endswith('.js'):
            return H.script(type="text/javascript", src=file_path)
        elif file_path.endswith('.css'):
            return H.link(rel="stylesheet", type="text/css", href=file_path)
        elif file_path.endswith('.ico'):
            return H.link(rel="icon", type="image/x-icon", href=file_path)
        else:
            raise ValueError('Included file ending is not supported in H.Include' + file_path)


class Include(H):
    def construct(self, file_path, *args, **kwargs):
        warnings.warn('Include will be deprecated, use Require instead', PendingDeprecationWarning)
        return Require().construct(file_path)

class Import(H):
    def construct(self, file_path, *args, **kwargs):
        warnings.warn('Import will be deprecated, use Require instead', PendingDeprecationWarning)
        return Require().construct(file_path)