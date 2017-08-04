#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from troposphere import Template, Parameter, Ref, Output, GetAtt, Tags, Join
from troposphere.ec2 import Instance, SecurityGroup, SecurityGroupRule
from troposphere.route53 import RecordSetType


class OpenVPN(object):
    def __init__(self, sceptre_user_data):
        self.sceptre_user_data = sceptre_user_data
        self.template = Template()
        self._add_parameters()
        self._add_resources()
        self._add_outputs()

    def _add_parameters(self):
        self.stack_prefix = Parameter(
            "StackPrefix",
            Type="String",
        )
        self.template.add_parameter(self.stack_prefix)

        self.ami_id = Parameter(
            "AmiId",
            Type="String",
            Default="ami-86c3c9e2",
        )
        self.template.add_parameter(self.ami_id)

        self.vpc_id_param = Parameter(
            "VpcId",
            Type="String",
        )
        self.template.add_parameter(self.vpc_id_param)

        self.key_name = Parameter(
            "KeyName",
            Type="String",
            Default="adrian.fernandez",
        )
        self.template.add_parameter(self.key_name)

        self.ssh_ip = Parameter(
            "SSHIP",
            Type="String",
            Default="10.0.0.0/8",
        )
        self.template.add_parameter(self.ssh_ip)

        self.public_subnet_id = Parameter(
            "PublicSubnetId",
            Type="String",
        )
        self.template.add_parameter(self.public_subnet_id)

    def _add_resources(self):
        rules = [("tcp", 443),
                 ("tcp", 943),
                 ("udp", 1194)]

        if self.sceptre_user_data['enable_ssh']:
            rules.append(("tcp", 22))
        self.openvpn_sg = SecurityGroup(
            "SSHSecurityGroup",
            VpcId=Ref(self.vpc_id_param),
            GroupDescription="Enable SSH access via port 22",
            SecurityGroupIngress=[SecurityGroupRule(
                                  IpProtocol=protocol,
                                  FromPort=port,
                                  ToPort=port,
                                  CidrIp=Ref(self.ssh_ip),)
                                  for protocol, port in rules],
            Tags=Tags(
                Name=Join('-', [Ref(self.stack_prefix), "openvpn"])
            ),
        )
        self.template.add_resource(self.openvpn_sg)

        self.openvpn_instance = Instance(
            "OpenVPNInstance",
            ImageId=Ref(self.ami_id),
            InstanceType="t2.micro",
            KeyName=Ref(self.key_name),
            SecurityGroupIds=[Ref(self.openvpn_sg)],
            SourceDestCheck=False,
            SubnetId=Ref(self.public_subnet_id),
            Tags=Tags(
                Name=Join('-', [Ref(self.stack_prefix), "openvpn"])
            ),
        )
        self.template.add_resource(self.openvpn_instance)

    def _add_outputs(self):
        self.openvpn_public_ip = Output(
            "OpenVpnPublicIp",
            Description="Public IP of the OpenVPN instance",
            Value=GetAtt(self.openvpn_instance, "PublicIp"),
        )
        self.template.add_output(self.openvpn_public_ip)

        self.openvpn_instance_id = Output(
            "OpenVPNInstanceId",
            Description="InstanceId of the newly created EC2 instance",
            Value=Ref(self.openvpn_instance),
        )
        self.template.add_output(self.openvpn_instance_id)


def sceptre_handler(sceptre_user_data):
    openvpn = OpenVPN(sceptre_user_data)
    return openvpn.template.to_json()
