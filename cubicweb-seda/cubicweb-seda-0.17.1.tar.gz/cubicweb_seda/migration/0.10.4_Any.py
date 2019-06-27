from __future__ import print_function

from cubicweb_seda import seda_profile_container_def, iter_all_rdefs

for etype, parent_rdefs in seda_profile_container_def(schema):
    sync_schema_props_perms(etype, syncprops=False)

for rdef, role in iter_all_rdefs(schema, 'SEDAArchiveTransfer'):
    try:
        fsschema[rdef.rtype].rdefs[(rdef.subject, rdef.object)]
    except KeyError:
        print('junk detected in database schema', rdef)
    else:
        sync_schema_props_perms((str(rdef.subject), str(rdef.rtype), str(rdef.object)),
                                syncprops=False)
