import os
from peek_server.server.sw_upload.PeekSwUploadResource import PeekSwUploadResource
from txhttputil.site.FileUnderlayResource import FileUnderlayResource

from vortex.VortexFactory import VortexFactory

adminSiteRoot = FileUnderlayResource()

def setupAdminSite():
    # Setup properties for serving the site
    adminSiteRoot.enableSinglePageApplication()

    import peek_admin
    frontendProjectDir = os.path.dirname(peek_admin.__file__)
    buildDir = os.path.join(frontendProjectDir, 'build-web', 'dist')

    buildDirParent = os.path.dirname(buildDir)
    if not os.path.isdir(buildDirParent):
        raise NotADirectoryError(buildDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(buildDir, exist_ok=True)

    adminSiteRoot.addFileSystemRoot(buildDir)

    # Create the Admin UI vortex
    from peek_platform import PeekPlatformConfig
    VortexFactory.createServer(PeekPlatformConfig.componentName, adminSiteRoot)

    # Add the platform update upload resource
    adminSiteRoot.putChild(b'peek_server.update.platform',
                           PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLATFORM))

    # Add the plugin update upload resource
    adminSiteRoot.putChild(b'peek_server.update.plugin',
                           PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLUGIN))