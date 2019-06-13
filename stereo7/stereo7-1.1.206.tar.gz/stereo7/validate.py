import fileutils
import validator_xml

import validate_maps
import validator_localization
import validate_sounds
import validate_units


def print_log(validator, caption):
    print caption
    result = validator.validate()
    for i, log in enumerate(sorted(validator.logs)):
        print '\t', str(i + 1) + '\t: ', log
    if not validator.logs:
        print '\tSuccess'
    return result


def run():
    result = True
    fileutils.ignore_folders.extend(['steam', 'cocoscenes'])
    fileutils.inspectResources()

    # validate xmls
    for file in fileutils.xmls:
        validator_xml.validate(file)
    logs = sorted(validator_xml.logs)
    for i, log in enumerate(logs):
        print '\t', str(i + 1) + '\t: ', log
    print '{} errors in {} xmls'.format(len(logs), len(fileutils.xmls))
    print 'Unused atlases:\n\t', '\n\t'.join(fileutils.unused) if len(fileutils.unused) else ' not founded'

    print_log(validate_maps, 'Validate maps:')
    print_log(validate_sounds, 'Validate sounds:')
    print_log(validate_units, 'Validate sounds:')
    vl = print_log(validator_localization, 'Validate localization:')

    result = result and len(validator_xml.logs) == 0
    result = result and len(validate_maps.logs) == 0
    result = result and len(validate_units.logs) == 0
    result = result and vl
    if not result:
        print 'Validation finished with Failed result'
        exit(-1)
    print 'Validation finished.'


if __name__ == '__main__':
    run()
