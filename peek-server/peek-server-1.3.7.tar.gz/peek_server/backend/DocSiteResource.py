import os

from txhttputil.site.FileUnderlayResource import FileUnderlayResource

docSiteRoot = FileUnderlayResource()


def setupDocSite():
    # Setup properties for serving the site
    docSiteRoot.enableSinglePageApplication()

    import peek_doc_admin
    docProjectDir = os.path.dirname(peek_doc_admin.__file__)
    distDir = os.path.join(docProjectDir, 'doc_dist')

    buildDirParent = os.path.dirname(distDir)
    if not os.path.isdir(buildDirParent):
        raise NotADirectoryError(buildDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    docSiteRoot.addFileSystemRoot(distDir)
