from pprint import pprint
import boto3


def list_streams_by_region(args):

    # use ec2 client get get all regions
    regions = [
        region["RegionName"]
        for region in boto3.client("ec2").describe_regions()["Regions"]
    ]

    for region in regions:

        client = boto3.Session().client("kinesis", region_name=region)

        try:
            while True:
                response = client.list_streams()
                if response["StreamNames"]:
                    print()
                    print("Region:", region)
                    print()
                    pprint(response["StreamNames"])
                if not response["HasMoreStreams"]:
                    break
        except Exception:  # pylint: disable=broad-except
            # May not have permission in region
            # So skip permission errors
            pass
