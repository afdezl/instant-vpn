#!/usr/bin/env python

from __future__ import unicode_literals

from troposphere import Template, Parameter, Ref, Output, GetAtt, Tags, Join, FindInMap
from troposphere.ec2 import Instance, SecurityGroup, SecurityGroupRule


OPENVPN_AMI_MAPPING = {
    "us-east-1": {"AMI": "ami-f6eed4e0"},
    "us-west-1": {"AMI": "ami-091f3069"},
    "us-west-2": {"AMI": "ami-e346559a"},
    "eu-west-1": {"AMI": "ami-238b6a5a"},
    "eu-west-2": {"AMI": "ami-17c5d373"},
    "sa-east-1": {"AMI": "ami-930673ff"},
    "ap-southeast-1": {"AMI": "ami-3cd6c45f"},
    "ap-northeast-1": {"AMI": "ami-dee1fdb9"}
}


class OpenVPN(object):
    def __init__(self, sceptre_user_data):
        self.sceptre_user_data = sceptre_user_data
        self.template = Template()
        self.template.add_mapping('RegionMap', OPENVPN_AMI_MAPPING)
        self._add_parameters()
        self._add_resources()
        self._add_outputs()

    def _add_parameters(self):
        self.stack_prefix = Parameter(
            "StackPrefix",
            Type="String",
        )
        self.template.add_parameter(self.stack_prefix)

        self.vpc_id_param = Parameter(
            "VpcId",
            Type="String",
        )
        self.template.add_parameter(self.vpc_id_param)

        self.key_name = Parameter(
            "KeyName",
            Type="String",
        )
        self.template.add_parameter(self.key_name)

        self.ssh_ip = Parameter(
            "AccessIP",
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
            ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
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
