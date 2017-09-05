#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from troposphere import Template, Parameter, Ref, Join, Output 
from troposphere.route53 import RecordSetType


class Route53RecordSets(object):
    def __init__(self, sceptre_user_data):
        self.sceptre_user_data = sceptre_user_data
        self.template = Template()
        self._add_parameters()
        self._add_resources()
        self._add_outputs()

    def _add_parameters(self):
        self.hosted_zone = Parameter(
            "HostedZone",
            Type="String",
        )
        self.template.add_parameter(self.hosted_zone)

        self.vpn_public_ip = Parameter(
            "VPNPublicIp",
            Type="String",
        )
        self.template.add_parameter(self.vpn_public_ip)

    def _add_resources(self):
        self.vpn_recordset = RecordSetType(
            "VPNRecordSet",
            HostedZoneName=Ref(self.hosted_zone),
            Name=Join(".", ["vpn", Ref(self.hosted_zone)]),
            Type="A",
            TTL=60,
            ResourceRecords=[Ref(self.vpn_public_ip)],
        )
        self.template.add_resource(self.vpn_recordset)

    def _add_outputs(self):
        self.vpn_public_ip_output = Output(
            "OpenVpnPublicIp",
            Description="Public IP of the OpenVPN instance",
            Value=Ref(self.vpn_public_ip),
        )
        self.template.add_output(self.vpn_public_ip_output)


def sceptre_handler(sceptre_user_data):
    recordsets = Route53RecordSets(sceptre_user_data)
    return recordsets.template.to_json()
