import logging
import requests
import urllib3
from enum import Enum

from kube_hunter.core.types import Discovery
from kube_hunter.core.events import handler
from kube_hunter.core.events.types import OpenPortEvent, Event, Service

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

""" Services """
class ReadOnlyKubeletEvent(Service, Event):
    """The read-only port on the kubelet serves health probing endpoints,
    and is relied upon by many kubernetes components"""
    def __init__(self):
        Service.__init__(self, name="Kubelet API (readonly)")


class SecureKubeletEvent(Service, Event):
    """The Kubelet is the main component in every Node,
    all pod operations goes through the kubelet"""
    def __init__(self, cert=False, token=False, anonymous_auth=True, **kwargs):
        self.cert = cert
        self.token = token
        self.anonymous_auth = anonymous_auth
        Service.__init__(self, name="Kubelet API", **kwargs)


class KubeletPorts(Enum):
    SECURED = 10250
    READ_ONLY = 10255


@handler.subscribe(OpenPortEvent, predicate= lambda x: x.port == 10255 or x.port == 10250)
class KubeletDiscovery(Discovery):
    """Kubelet Discovery
    Checks for the existence of a Kubelet service, and its open ports
    """
    def __init__(self, event):
        self.event = event

    def get_read_only_access(self):
        logger.debug("Passive hunter is attempting to get kubelet "
                     f"read access at {self.event.host}:{self.event.port}")
        r = requests.get(f"http://{self.event.host}:{self.event.port}/pods")
        if r.status_code == 200:
            self.publish_event(ReadOnlyKubeletEvent())

    def get_secure_access(self):
        logger.debug("Attempting to get kubelet secure access")
        ping_status = self.ping_kubelet()
        if ping_status == 200:
            self.publish_event(SecureKubeletEvent(secure=False))
        elif ping_status == 403:
            self.publish_event(SecureKubeletEvent(secure=True))
        elif ping_status == 401:
            self.publish_event(SecureKubeletEvent(secure=True, anonymous_auth=False))

    def ping_kubelet(self):
        logger.debug("Attempting to get pod info from kubelet")
        try:
            return requests.get(f"https://{self.event.host}:{self.event.port}/pods",
                                verify=False).status_code
        except Exception as ex:
            logger.debug("Failed pinging https port 10250 on "
                         f"{self.event.host} : {ex}", exc_info=True)

    def execute(self):
        if self.event.port == KubeletPorts.SECURED.value:
            self.get_secure_access()
        elif self.event.port == KubeletPorts.READ_ONLY.value:
            self.get_read_only_access()
