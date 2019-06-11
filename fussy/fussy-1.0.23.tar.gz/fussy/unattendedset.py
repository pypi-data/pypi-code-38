#! /usr/bin/env python
"""Create .deb sets from unattended upgrade"""
from __future__ import print_function
from fussy import nbio, twrite
import re, os, time, logging, json
import tarfile
log = logging.getLogger(__name__)
TARGET_MATCHER = re.compile(r"""DestFile:['](?P<filename>[^']+)[']""")
DEPENDENCY_MATCHER = re.compile(r"""(?P<package>[^, ()]*?)[ ]*[(](?P<compare>[<>=]+)[ ]*(?P<version>[^)]*?)[)]""")
DIGIT_FINDER = re.compile( '\d+' )
def parse_dpkg_info( content ):
    versions = {}
    content = content.strip().splitlines()
    current = None
    for line in content:
        for interesting in [
            'Package:', 'Version:', 'Status:', 
            'Depends:','Pre-Depends:', 'Architecture:'
        ]:
            line = line.strip()
            if line.startswith(interesting):
                value = line[len(interesting):].strip()
                if interesting == 'Package:':
                    if current:
                        versions[current['package']] = current
                    current = dict( package = value )
                elif interesting == 'Version:':
                    version = line.split(':', 1)[1].strip()
                    current['version'] = [ 
                        int(x,10) 
                        for x in DIGIT_FINDER.findall( version )
                    ]
                elif interesting == 'Status:':
                    if 'installed' in value.split():
                        current['installed'] = True 
                    else:
                        current['installed'] = False
                elif interesting in ('Depends:','Pre-Depends:'):
                    value= [
                        x.groupdict() 
                        for x in DEPENDENCY_MATCHER.finditer( value )
                    ]
                    if interesting is 'Depends:':
                        key = 'depends'
                    else:
                        key = 'predepends'
                    current[key] = value
                else:
                    current[interesting.lower().rstrip(':')] = value
    if current:
        versions[current['package']] = current
    return versions

def get_options():
    import argparse
    parser = argparse.ArgumentParser(description='Process unattended upgrade log to produce upgrade set')
    default_file = 'os-upgrades-%s.deb.tar'%(time.strftime('%Y-%m-%d-%H-%M', time.gmtime()))
    parser.add_argument(
        '--target', metavar='FILENAME.deb.tar',
        default = default_file, 
        help="Target directory to watch (must exist), default: %s"%(default_file, ),
    )
    parser.add_argument(
        '--list',  action='store_true', 
        default=False, 
        help = "Just list the files that would be packed, do not do actual packing", 
    )
    parser.add_argument(
        '--exclude', metavar='PACKAGE', 
        dest = 'excluded', 
        action = 'append', 
        help='Packages *not* to include in the resulting tar-file', 
    )
    parser.add_argument(
        '--recalculate', action='store_true', 
        default=False, 
        help='If provided, will run unattended upgrades with dry-run to calculate (and download) the set', 
    )
    return parser

def get_metadata_options():
    import argparse
    parser = argparse.ArgumentParser(description='Extract metadata from .deb files for unattended set')
    parser.add_argument(
        '-m',
        '--merge',
        metavar='FULLPATH.json',
        default=None,
        help='If provided, metadata will be *merged* into existing json file',
    )
    parser.add_argument(
        'filenames',
        metavar='FULLPATH.deb',
        nargs = "+",
    )
    return parser

def recalculate():
    log.warning("Running unattended upgrades, this will take a long time")
    nbio.Process('sudo unattended-upgrades -d --dry-run')()

def filter_exclusions( package, excluded ):
    import fnmatch
    for exclude in excluded:
        if fnmatch.fnmatch( package, exclude ):
            log.info("Excluding %s due to pattern %s", package, exclude)
            return False 
    return True

def get_components(excluded=None):
    result = []
    unique = set()
    for line in nbio.Process(
        """grep '/var/cache/apt/archives' /var/log/unattended-upgrades/unattended-upgrades.log | grep -v check_conffile | grep AcquireItem"""
    )().splitlines():
        match = TARGET_MATCHER.search(line)
        if match:
            filename = match.group('filename')
            base = os.path.basename(filename)
            # Use package name + Architecture (i.e. amd64, i386, all)
            package = '_'.join([base.split('_')[0], base.split('_')[-1]])
            if package in unique:
                continue
            unique.add(package)
            if excluded:
                if filter_exclusions( package, excluded ):
                    result.append( filename )
            else:
                result.append( filename )
    return result

def metadata_main():
    options = get_metadata_options().parse_args()
    structure = metadata_structure( options.filenames )
    if options.merge:
        new_set = dict([(s['package'],s) for s in structure['metadata']])
        final_set = []
        previous = json.loads(open(options.merge).read())
        for item in previous['metadata']:
            if item['package'] in new_set:
                log.info("Updating record for %s",item['package'])
                item = new_set.pop(item['package'])
            final_set.append( item )
        final_set.extend( new_set.values())
        structure['metadata'] = final_set
        previous.update(structure)
        structure = previous
    print(json.dumps(structure,indent=2))
    
def metadata_structure( filenames ):
    metadata_list = []
    for package in filenames:
        metadata_list.append( metadata(package))
    return {
        'metadata': metadata_list, 
        'ts': time.time(), 
    }

def metadata( filename ):
    command = ['dpkg', '--info', filename]
    
    output = nbio.Process(command)()
    for record in parse_dpkg_info(output).values():
        record['filename'] = os.path.basename(filename)
        return record 
    raise RuntimeError("Unable to extract metadata for %r"%(filename, ))

def pack_zip(target='os-upgrades.deb.tar', excluded=None):
    log.info("Packing into target: %r", target)
    t = tarfile.TarFile(target, mode='w')
    try:
        packages = get_components(excluded=excluded)
        for package in packages:
            log.info("Packing: %s", package)
            t.add( package, os.path.basename(package) )
        structure = metadata_structure( packages )
        try:
            twrite.twrite( target + '.json', json.dumps(structure))
            t.add( target+'.json',  'metadata.json' )
        finally:
            os.remove( target + '.json' )
    finally:
        t.close()

def main():
    logging.basicConfig(level=logging.INFO)
    options = get_options().parse_args()
    if options.recalculate:
        recalculate()
    if options.list:
        for package in get_components(excluded=options.excluded):
            base = os.path.basename(package)
            package, version = base.split('_', 1)
            print( '%s\t%s'%(package, version))
        return
    pack_zip( target=options.target,  excluded=options.excluded )
    return 0

if __name__ == "__main__":
    main()
