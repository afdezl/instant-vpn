#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from troposphere import Template, Parameter, Ref, Output, Tags
from troposphere.ec2 import VPC, InternetGateway, VPCGatewayAttachment


PARAMETERS = {
    "StackPrefix": {
        "Type": "String"
    },
    "CidrBlock": {
        "Type": "String",
        "Default": "10.0.0.0/16"
    }
}


class AFVPC(object):
    def __init__(self, sceptre_user_data):
        self.sceptre_user_data = sceptre_user_data
        self.template = Template()
        self.parameters = {}
        self._add_parameters(PARAMETERS)
        self._add_resources()
        self._add_outputs()

    def _add_parameters(self, parameters={}):
        for param, info in parameters.items():
            self.parameters[param] = Parameter(param, **info)
            self.template.add_parameter(self.parameters[param])

    def _add_resources(self):
        self.vpc = VPC(
            "VirtualPrivateCloud",
            CidrBlock=Ref(self.parameters['CidrBlock']),
            InstanceTenancy="default",
            EnableDnsSupport=True,
            EnableDnsHostnames=True,
            Tags=Tags(
                Name=Ref(self.parameters['StackPrefix'])
            ),
        )
        self.template.add_resource(self.vpc)
        self.igw = InternetGateway(
            "InternetGateway",
        )
        self.template.add_resource(self.igw)
        self.igw_attachment = VPCGatewayAttachment(
            "IGWAttachment",
            VpcId=Ref(self.vpc),
            InternetGatewayId=Ref(self.igw),
        )
        self.template.add_resource(self.igw_attachment)

    def _add_outputs(self):
        self.vpc_id_output = Output(
            "VpcId",
            Description="VPC ID",
            Value=Ref(self.vpc)
        )
        self.template.add_output(self.vpc_id_output)

        self.igw_id_output = Output(
            "IgwId",
            Description="IGW ID",
            Value=Ref(self.igw)
        )
        self.template.add_output(self.igw_id_output)


def sceptre_handler(sceptre_user_data):
    vpc = AFVPC(sceptre_user_data)
    return vpc.template.to_json()
