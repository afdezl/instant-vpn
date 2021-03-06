from __future__ import print_function

from datetime import datetime

import boto3
import json
import os

ec2 = boto3.client("ec2")
TO_STOP = os.environ.get("TO_STOP")

def main(event, context):
    schedules = {}
    resp = ec2.describe_instances(InstanceIds=[TO_STOP])

    schedules = {instance["InstanceId"]: instance["State"].get("Name")
                 for reservation in resp["Reservations"]
                 for instance in reservation["Instances"]}
    response = {'items': []}
    for k, v in schedules.items():
        if v not in ["stopped", "terminated"]:
            ec2.stop_instances(InstanceIds=[k])
            response['items'].append({'InstanceId': k, 'Action': 'STOPPED'})
        else:
            response['items'].append({'InstanceId': k, 'Action': None})
    print(datetime.now().isoformat(), response)
    return json.dumps(response)
