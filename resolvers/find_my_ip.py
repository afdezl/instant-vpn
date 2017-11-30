from sceptre.resolvers import Resolver
from json import load
from six.moves.urllib.request import urlopen


class FindMyIp(Resolver):
    def __init__(self, *args, **kwargs):
        super(FindMyIp, self).__init__(*args, **kwargs)

    def resolve(self):
        my_ip = load(urlopen('https://api.ipify.org/?format=json'))['ip']
        return "{}/32".format(my_ip)
