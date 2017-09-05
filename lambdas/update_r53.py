from __future__ import print_function

from datetime import datetime

import boto3
import json
import os


ec2 = boto3.client('ec2')
route53 = boto3.client('route53')

HOSTED_ZONE_ID = os.environ.get("HOSTED_ZONE_ID")
RECORDSET = os.environ.get("RECORDSET")


def main(event, context):
    instance_id = event["detail"]["instance-id"]
    response = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]

    print(datetime.now().isoformat(),
          "Updating {0} A record in hosted zone {1}.".format(RECORDSET,
                                                             HOSTED_ZONE_ID))

    route53.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": RECORDSET,
                        "Type": "A",
                        "TTL": 60,
                        "ResourceRecords": [{
                            "Value": public_ip}
                        ]
                    }
                }
            ]
        })

    print(datetime.now().isoformat(),
          "{0} Record updated with value {1}".format(RECORDSET, public_ip))
    return True
