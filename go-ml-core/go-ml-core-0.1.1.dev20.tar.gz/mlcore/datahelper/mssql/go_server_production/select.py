get_vm_list = """
SELECT Id, Latitude, Longitude, LocName
FROM dbo.Vm vm
LEFT JOIN dbo.VmExt vmExt ON vm.Id = vmExt.vmId
WHERE (STATE = 1 OR STATE = 0 OR STATE = 99 OR STATE = 100)
    AND vmExt.vmId IS NULL
"""