def install(packages, release=None):
    return "apt-get -y{release}install {packages}".format(
        release=' -t %s' % release if release else ' ',
        packages=" ".join(packages))


def import_apt_key_from_url(url):
    """
    Import a GPG key for a repository into apt's keychain from given url
    """
    return 'wget -qO - {url} | apt-key add -'.format(url=url)


def repo_sources_line(uri, distro, components):
    return "deb {uri} {distro} {components}".format(
        uri=uri,
        distro=distro,
        components=components)


def update():
    """
    Update package index
    """
    return "apt-get update"
