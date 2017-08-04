#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

from troposphere import Template, Parameter, Ref, Output, Tags, Join
from troposphere.ec2 import Subnet
from troposphere.ec2 import Route
from troposphere.ec2 import RouteTable
from troposphere.ec2 import SubnetRouteTableAssociation


PARAMETERS = {
    "StackPrefix": {
        "Type": "String"
    },
    "VpcId": {
        "Type": "String"
    },
    "IgwId": {
        "Type": "String"
    },
    "Az1": {
        "Type": "String",
        "Default": "eu-west-1a"
    },
    "Az2": {
        "Type": "String",
        "Default": "eu-west-1b"
    },
    "PubSubnet1CidrBlock": {
        "Type": "String",
        "Default": "10.0.1.0/24"
    },
    "PubSubnet2CidrBlock": {
        "Type": "String",
        "Default": "10.0.2.0/24"
    },
    "PrivSubnet1CidrBlock": {
        "Type": "String",
        "Default": "10.0.11.0/24"
    },
    "PrivSubnet2CidrBlock": {
        "Type": "String",
        "Default": "10.0.12.0/24"
    },
}


class Subnets(object):
    def __init__(self, sceptre_user_data):
        self.sceptre_user_data = sceptre_user_data
        self.template = Template()
        self.parameters = {}
        self.public_subnets = {}
        self.private_subnets = {}
        self._add_parameters(PARAMETERS)
        self._add_subnets()
        self._add_route_tables()
        self._add_outputs()

    def _add_parameters(self, parameters={}):
        for param, info in parameters.items():
            self.parameters[param] = Parameter(param, **info)
            self.template.add_parameter(self.parameters[param])

    def _add_subnets(self):
        public_key = "PubSubnet"
        private_key = "PrivSubnet"

        for i, key in enumerate([p
                                for p in self.parameters
                                if p.startswith(public_key)]):
            name = public_key + str(i+1)
            self.public_subnets[name] = Subnet(
                name,
                CidrBlock=Ref(self.parameters[key]),
                VpcId=Ref(self.parameters['VpcId']),
                AvailabilityZone=Ref(self.parameters['Az' + str(i+1)]),
                MapPublicIpOnLaunch=True,
                Tags=Tags(
                    Name=Join('-', [Ref(self.parameters['StackPrefix']),
                                    "pub",
                                    Ref(self.parameters['Az' + str(i+1)])])
                ),
            )
            self.template.add_resource(self.public_subnets[name])

        for i, key in enumerate([p
                                for p in self.parameters
                                if p.startswith(private_key)]):
            name = private_key + str(i+1)
            self.private_subnets[name] = Subnet(
                name,
                CidrBlock=Ref(self.parameters[key]),
                VpcId=Ref(self.parameters['VpcId']),
                AvailabilityZone=Ref(self.parameters['Az' + str(i+1)]),
                MapPublicIpOnLaunch=True,
                Tags=Tags(
                    Name=Join('-', [Ref(self.parameters['StackPrefix']),
                                    "priv",
                                    Ref(self.parameters['Az' + str(i+1)])])
                ),
            )
            self.template.add_resource(self.private_subnets[name])

    def _add_route_tables(self):
        self.routeTable = RouteTable(
            'RouteTable',
            VpcId=Ref(self.parameters['VpcId']),
            Tags=Tags(
                Name=Join('-', [Ref(self.parameters['StackPrefix']), "public"])
            ),
        )
        self.template.add_resource(self.routeTable)

        self.public_route = Route(
            'Route',
            GatewayId=Ref(self.parameters['IgwId']),
            DestinationCidrBlock='0.0.0.0/0',
            RouteTableId=Ref(self.routeTable),
        )
        self.template.add_resource(self.public_route)

        self.subnetRouteTableAssociation1 = SubnetRouteTableAssociation(
            'PubSubnetRouteTableAssociation1',
            SubnetId=Ref(self.public_subnets['PubSubnet1']),
            RouteTableId=Ref(self.routeTable),
        )
        self.template.add_resource(self.subnetRouteTableAssociation1)

        self.subnetRouteTableAssociation2 = SubnetRouteTableAssociation(
            'PubSubnetRouteTableAssociation2',
            SubnetId=Ref(self.public_subnets['PubSubnet2']),
            RouteTableId=Ref(self.routeTable),
        )
        self.template.add_resource(self.subnetRouteTableAssociation2)

    def _add_outputs(self):
        self.pub_subnet1_id_output = Output(
            "PubSubnet1Id",
            Description="Public subnet 1",
            Value=Ref(self.public_subnets['PubSubnet1'])
        )
        self.template.add_output(self.pub_subnet1_id_output)

        self.pub_subnet2_id_output = Output(
            "PubSubnet2Id",
            Description="Public subnet 2",
            Value=Ref(self.public_subnets['PubSubnet2'])
        )
        self.template.add_output(self.pub_subnet2_id_output)

        self.priv_subnet1_id_output = Output(
            "PrivSubnet1Id",
            Description="Private subnet 1",
            Value=Ref(self.private_subnets['PrivSubnet1'])
        )
        self.template.add_output(self.priv_subnet1_id_output)

        self.priv_subnet2_id_output = Output(
            "PrivsSubnet2Id",
            Description="Private subnet 2",
            Value=Ref(self.private_subnets['PrivSubnet1'])
        )
        self.template.add_output(self.priv_subnet2_id_output)


def sceptre_handler(sceptre_user_data):
    subnets = Subnets(sceptre_user_data)
    return subnets.template.to_json()
