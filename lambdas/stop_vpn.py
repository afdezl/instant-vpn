from __future__ import print_function

from datetime import datetime

import boto3
import json

EC2_CLIENT = boto3.client("ec2")
TO_STOP = ["afdezl-openvpn"]


def main(event, context):
    schedules = {}
    resp = EC2_CLIENT.describe_instances(
        Filters=[{"Name": 'tag:Name',
                  "Values": TO_STOP}, ])

    schedules = {instance["InstanceId"]: instance["State"].get("Name")
                 for reservation in resp["Reservations"]
                 for instance in reservation["Instances"]}
    response = {'items': []}
    for k, v in schedules.items():
        if v not in ["stopped", "terminated"]:
            EC2_CLIENT.stop_instances(InstanceIds=[k])
            response['items'].append({'InstanceId': k, 'Action': 'STOPPED'})
        else:
            response['items'].append({'InstanceId': k, 'Action': None})
    print(datetime.now().isoformat(), response)
    return json.dumps(response)
