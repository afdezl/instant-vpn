from sceptre.resolvers import Resolver
from json import load
from urllib2 import urlopen


class FindVpnIp(Resolver):
    def __init__(self, *args, **kwargs):
        super(FindVpnIp, self).__init__(*args, **kwargs)

    def resolve(self):
        response = self.connection_manager.call(
            service="ec2",
            command="describe_instances",
            kwargs={
                "Filters": [
                    {
                        "Name": "tag:Name",
                        "Values": [self.argument]
                    },
                    {
                        "Name": "instance-state-name",
                        "Values": ["running"]
                    }
                ]
            }
        )
        vpn_ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        return vpn_ip
