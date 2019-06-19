
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.vmware import PyVmomi
from ansible.module_utils.vmware_rest_client import VmwareRestClient
try:
    from com.vmware.cis.tagging_client import (Category, Tag, TagAssociation, CategoryModel)
    from com.vmware.vapi.std_client import DynamicID
except ImportError:
    pass

import logging

logger = logging.getLogger('vmware')
hdlr = logging.FileHandler('/tmp/ansible-vmware.log')
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

class VmwareTag(VmwareRestClient):
    def __init__(self, module):
        super(VmwareTag, self).__init__(module)
        self.tag_service = Tag(self.connect)
        self.tag_association = TagAssociation(self.connect)
        self.global_tags = dict()
        self.tag_name = self.params.get('tag_name')

        # for id in Category(self.connect).list():
        #     cat = Category(self.connect).get(id)
        #     logger.info(" \"%s\": %s" % (cat.name,id))


    def apply_tags(self, vm, category_ids, tags):

        dynamic_id = DynamicID(type='VirtualMachine', id=vm)
        attached = []

        for tag in self.tag_service.list():
            tag_obj = self.tag_service.get(tag)
            self.global_tags[tag_obj.category_id + tag_obj.name.lower()] = dict(tag_description=tag_obj.description,
                                                  tag_used_by=tag_obj.used_by,
                                                  tag_category_id=tag_obj.category_id,
                                                  tag_id=tag_obj.id
                                                  )

        logger.info(len(self.global_tags))
        for tag_id in self.tag_association.list_attached_tags(dynamic_id):
            attached.append(tag_id)

        for id in tags:
            key = category_ids[id] + tags[id].lower()
            if key not in self.global_tags:
                logger.info("Creating new tag: " + key)
                create_spec = self.tag_service.CreateSpec()
                create_spec.name = tags[id]
                create_spec.description = tags[id]
                create_spec.category_id = category_ids[id]
                tag = self.tag_service.create(create_spec)
            tag = self.global_tags[key]
            if tag['tag_id'] in attached:
                logger.info("Skipping " + id)
            else:
                logger.info("Applying %s (%s)=%s (%s) on %s" % (id,category_ids[id], tags[id],tag['tag_id'], vm))
                self.tag_association.attach(tag_id=tag['tag_id'], object_id=dynamic_id)

        for tag_id in self.tag_association.list_attached_tags(dynamic_id):
            attached.append(tag_id)
        return attached


def main():
    argument_spec = VmwareRestClient.vmware_client_argument_spec()
    argument_spec.update(
        vm=dict(type='str', required=True),
        uuid=dict(type='str', required=True),
        tags=dict(type='dict', required=True),
        category_ids=dict(type='dict', required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec)
    pyv = PyVmomi(module)
    vm = pyv.get_vm()
    vmware_tag = VmwareTag(module)
    result = vmware_tag.apply_tags(vm._moId, module.params['category_ids'], module.params['tags'])
    module.exit_json()


if __name__ == '__main__':
    main()