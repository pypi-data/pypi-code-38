# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import json
import warnings
import pulumi
import pulumi.runtime
from .. import utilities, tables

class VirtualMachine(pulumi.CustomResource):
    availability_set_id: pulumi.Output[str]
    """
    The ID of the Availability Set in which the Virtual Machine should exist. Changing this forces a new resource to be created.
    """
    boot_diagnostics: pulumi.Output[dict]
    """
    A `boot_diagnostics` block.
    """
    delete_data_disks_on_termination: pulumi.Output[bool]
    """
    Should the Data Disks (either the Managed Disks / VHD Blobs) be deleted when the Virtual Machine is destroyed? Defaults to `false`.
    """
    delete_os_disk_on_termination: pulumi.Output[bool]
    """
    Should the OS Disk (either the Managed Disk / VHD Blob) be deleted when the Virtual Machine is destroyed? Defaults to `false`.
    """
    identity: pulumi.Output[dict]
    """
    A `identity` block.
    """
    license_type: pulumi.Output[str]
    """
    Specifies the BYOL Type for this Virtual Machine. This is only applicable to Windows Virtual Machines. Possible values are `Windows_Client` and `Windows_Server`.
    """
    location: pulumi.Output[str]
    """
    Specifies the Azure Region where the Virtual Machine exists. Changing this forces a new resource to be created.
    """
    name: pulumi.Output[str]
    """
    Specifies the name of the Virtual Machine. Changing this forces a new resource to be created.
    """
    network_interface_ids: pulumi.Output[list]
    """
    A list of Network Interface ID's which should be associated with the Virtual Machine.
    """
    os_profile: pulumi.Output[dict]
    """
    An `os_profile` block. Required when `create_option` in the `storage_os_disk` block is set to `FromImage`.
    """
    os_profile_linux_config: pulumi.Output[dict]
    """
    A `os_profile_linux_config` block.
    """
    os_profile_secrets: pulumi.Output[list]
    """
    One or more `os_profile_secrets` blocks.
    """
    os_profile_windows_config: pulumi.Output[dict]
    """
    A `os_profile_windows_config` block.
    """
    plan: pulumi.Output[dict]
    """
    A `plan` block.
    """
    primary_network_interface_id: pulumi.Output[str]
    """
    The ID of the Network Interface (which must be attached to the Virtual Machine) which should be the Primary Network Interface for this Virtual Machine.
    """
    resource_group_name: pulumi.Output[str]
    """
    Specifies the name of the Resource Group in which the Virtual Machine should exist. Changing this forces a new resource to be created.
    """
    storage_data_disks: pulumi.Output[list]
    """
    One or more `storage_data_disk` blocks.
    """
    storage_image_reference: pulumi.Output[dict]
    """
    A `storage_image_reference` block.
    """
    storage_os_disk: pulumi.Output[dict]
    """
    A `storage_os_disk` block.
    """
    tags: pulumi.Output[dict]
    """
    A mapping of tags to assign to the Virtual Machine.
    """
    vm_size: pulumi.Output[str]
    """
    Specifies the [size of the Virtual Machine](https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-size-specs/).
    """
    zones: pulumi.Output[str]
    """
    A list of a single item of the Availability Zone which the Virtual Machine should be allocated in.
    """
    def __init__(__self__, resource_name, opts=None, availability_set_id=None, boot_diagnostics=None, delete_data_disks_on_termination=None, delete_os_disk_on_termination=None, identity=None, license_type=None, location=None, name=None, network_interface_ids=None, os_profile=None, os_profile_linux_config=None, os_profile_secrets=None, os_profile_windows_config=None, plan=None, primary_network_interface_id=None, resource_group_name=None, storage_data_disks=None, storage_image_reference=None, storage_os_disk=None, tags=None, vm_size=None, zones=None, __name__=None, __opts__=None):
        """
        Manages a Virtual Machine.
        
        > **NOTE:** Data Disks can be attached either directly on the `azurerm_virtual_machine` resource, or using the `azurerm_virtual_machine_data_disk_attachment` resource - but the two cannot be used together. If both are used against the same Virtual Machine, spurious changes will occur.
        
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] availability_set_id: The ID of the Availability Set in which the Virtual Machine should exist. Changing this forces a new resource to be created.
        :param pulumi.Input[dict] boot_diagnostics: A `boot_diagnostics` block.
        :param pulumi.Input[bool] delete_data_disks_on_termination: Should the Data Disks (either the Managed Disks / VHD Blobs) be deleted when the Virtual Machine is destroyed? Defaults to `false`.
        :param pulumi.Input[bool] delete_os_disk_on_termination: Should the OS Disk (either the Managed Disk / VHD Blob) be deleted when the Virtual Machine is destroyed? Defaults to `false`.
        :param pulumi.Input[dict] identity: A `identity` block.
        :param pulumi.Input[str] license_type: Specifies the BYOL Type for this Virtual Machine. This is only applicable to Windows Virtual Machines. Possible values are `Windows_Client` and `Windows_Server`.
        :param pulumi.Input[str] location: Specifies the Azure Region where the Virtual Machine exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the Virtual Machine. Changing this forces a new resource to be created.
        :param pulumi.Input[list] network_interface_ids: A list of Network Interface ID's which should be associated with the Virtual Machine.
        :param pulumi.Input[dict] os_profile: An `os_profile` block. Required when `create_option` in the `storage_os_disk` block is set to `FromImage`.
        :param pulumi.Input[dict] os_profile_linux_config: A `os_profile_linux_config` block.
        :param pulumi.Input[list] os_profile_secrets: One or more `os_profile_secrets` blocks.
        :param pulumi.Input[dict] os_profile_windows_config: A `os_profile_windows_config` block.
        :param pulumi.Input[dict] plan: A `plan` block.
        :param pulumi.Input[str] primary_network_interface_id: The ID of the Network Interface (which must be attached to the Virtual Machine) which should be the Primary Network Interface for this Virtual Machine.
        :param pulumi.Input[str] resource_group_name: Specifies the name of the Resource Group in which the Virtual Machine should exist. Changing this forces a new resource to be created.
        :param pulumi.Input[list] storage_data_disks: One or more `storage_data_disk` blocks.
        :param pulumi.Input[dict] storage_image_reference: A `storage_image_reference` block.
        :param pulumi.Input[dict] storage_os_disk: A `storage_os_disk` block.
        :param pulumi.Input[dict] tags: A mapping of tags to assign to the Virtual Machine.
        :param pulumi.Input[str] vm_size: Specifies the [size of the Virtual Machine](https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-size-specs/).
        :param pulumi.Input[str] zones: A list of a single item of the Availability Zone which the Virtual Machine should be allocated in.
        """
        if __name__ is not None:
            warnings.warn("explicit use of __name__ is deprecated", DeprecationWarning)
            resource_name = __name__
        if __opts__ is not None:
            warnings.warn("explicit use of __opts__ is deprecated, use 'opts' instead", DeprecationWarning)
            opts = __opts__
        if not resource_name:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(resource_name, str):
            raise TypeError('Expected resource name to be a string')
        if opts and not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['availability_set_id'] = availability_set_id

        __props__['boot_diagnostics'] = boot_diagnostics

        __props__['delete_data_disks_on_termination'] = delete_data_disks_on_termination

        __props__['delete_os_disk_on_termination'] = delete_os_disk_on_termination

        __props__['identity'] = identity

        __props__['license_type'] = license_type

        __props__['location'] = location

        __props__['name'] = name

        if network_interface_ids is None:
            raise TypeError("Missing required property 'network_interface_ids'")
        __props__['network_interface_ids'] = network_interface_ids

        __props__['os_profile'] = os_profile

        __props__['os_profile_linux_config'] = os_profile_linux_config

        __props__['os_profile_secrets'] = os_profile_secrets

        __props__['os_profile_windows_config'] = os_profile_windows_config

        __props__['plan'] = plan

        __props__['primary_network_interface_id'] = primary_network_interface_id

        if resource_group_name is None:
            raise TypeError("Missing required property 'resource_group_name'")
        __props__['resource_group_name'] = resource_group_name

        __props__['storage_data_disks'] = storage_data_disks

        __props__['storage_image_reference'] = storage_image_reference

        if storage_os_disk is None:
            raise TypeError("Missing required property 'storage_os_disk'")
        __props__['storage_os_disk'] = storage_os_disk

        __props__['tags'] = tags

        if vm_size is None:
            raise TypeError("Missing required property 'vm_size'")
        __props__['vm_size'] = vm_size

        __props__['zones'] = zones

        super(VirtualMachine, __self__).__init__(
            'azure:compute/virtualMachine:VirtualMachine',
            resource_name,
            __props__,
            opts)


    def translate_output_property(self, prop):
        return tables._CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return tables._SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

