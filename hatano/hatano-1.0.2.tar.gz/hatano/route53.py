from hatano.errors import HatanoError

import boto3


class Route53:
    def __init__(self):
        self.r53 = boto3.client('route53')

    def get_hosted_zone(self, name):
        zones = self.r53.list_hosted_zones()['HostedZones']
        for zone in zones:
            if (name + '.').endswith(zone['Name']):
                return zone
        raise HatanoError(f"Hosted zone not found for {name}")

    def _change_cname_record(self, name, value, zone_id, action, typ, ttl):
        if action == "CREATE":
            comment = f'add {name} -> {value}'
            record = {
                    'Name': name,
                    'Type': typ,
                    'TTL': ttl,
                    'ResourceRecords': [{'Value': value}]
                    }
        else:
            comment = ""

        try:
            response = self.r53.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Comment': comment,
                'Changes': [
                    {
                        'Action': action,
                        'ResourceRecordSet': record
                        }
                    ]
                }
            )
        except Exception as e:
            print(e)

    def add_cname_record(self, name, value):
        zone = self.get_hosted_zone(name)
        zone_id = zone['Id']
        self._change_cname_record(name, value, zone_id, "CREATE", "CNAME", 60)

    def delete_cname_record(self, name):
        zone = self.get_hosted_zone(name)
        zone_id = zone['Id']
        recordsets = self.r53.list_resource_record_sets(
                HostedZoneId=zone_id)["ResourceRecordSets"]
        comment = f"delete {name}"
        for record in recordsets:
            if record['Name'] == name + '.':
                self.r53.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch={
                            'Comment': comment,
                            'Changes': [
                                {
                                    'Action': "DELETE",
                                    'ResourceRecordSet': record
                                    }
                                ]
                            }
                        )
                return
        print(f"record not found for {name}")



