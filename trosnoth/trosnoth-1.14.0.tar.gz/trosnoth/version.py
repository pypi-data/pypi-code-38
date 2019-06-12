version = '1.14.0'
release = True
revision = ''

if release:
    fullVersion = '%s' % (version,)
else:
    fullVersion = '%s-%s' % (version, revision)

titleVersion = 'Version %s' % (fullVersion,)
