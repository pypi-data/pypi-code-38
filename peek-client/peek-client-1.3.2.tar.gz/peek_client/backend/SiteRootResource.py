import os

from txhttputil.site.FileUnderlayResource import FileUnderlayResource

from peek_platform import PeekPlatformConfig

mobileRoot = FileUnderlayResource()

def setupMobile():
    # Setup properties for serving the site
    mobileRoot.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent

    import peek_mobile
    frontendProjectDir = os.path.dirname(peek_mobile.__file__)
    distDir = os.path.join(frontendProjectDir, 'build-web', 'dist')

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    mobileRoot.addFileSystemRoot(distDir)


desktopRoot = FileUnderlayResource()

def setupDesktop():
    # Setup properties for serving the site
    desktopRoot.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent

    import peek_desktop
    frontendProjectDir = os.path.dirname(peek_desktop.__file__)
    distDir = os.path.join(frontendProjectDir, 'build-web', 'dist')

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    desktopRoot.addFileSystemRoot(distDir)



docSiteRoot = FileUnderlayResource()

def setupDocSite():
    # Setup properties for serving the site
    docSiteRoot.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent

    import peek_doc_user
    docProjectDir = os.path.dirname(peek_doc_user.__file__)
    distDir = os.path.join(docProjectDir, 'doc_dist')

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    docSiteRoot.addFileSystemRoot(distDir)
