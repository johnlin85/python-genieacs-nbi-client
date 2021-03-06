"""genieacs.nbi.client."""

from typing import Dict, List
import urllib.request
from genieacs.nbi.utils import build_request, build_post_request


class Client:
    """GenieACS NBI Client."""

    address = "http://localhost:7557"
    timeout = 15
    verbose = False

    def __init__(self, **kwargs):
        """Initialize genieacs.nbi.client.Client."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def url(self, suffix, *args):
        """
        Prepare and return an url string.

        See format description at
        https://github.com/genieacs/genieacs/wiki/API-Reference

        return a string based on values of address, suffix and args
        """
        return "/".join(["{}", suffix]).format(self.address, *args)

    def devices_url(self, device_id=None):
        """Replace whitespaces by %20 and return devices/device_id."""
        infix = "devices"
        if device_id is None:
            return self.url(infix)
        return self.url(
            "{}/{}".format(infix, "{}".format(device_id).replace(' ', "%20")))

    def dispatch_device_task(self, device_id, data, connection_request=False):
        """Prepare and execute add task request."""
        url = "/".join([self.devices_url(device_id),
                        "tasks"])
        if connection_request:
            url += "?connection_request"

        req = build_post_request(url=url, data=data)
        return self.perform_request(req)

    def dispatch_preset(
            self,
            weight: int,
            preconditions: Dict,
            configurations: List[Dict]):
        """Prepare and execute add preset request."""
        data = {
            "weight": weight,
            "preconditions": preconditions,
            "configurations": configurations}
        req = build_post_request(url=self.url("presets"), data=data)
        return self.perform_request(req)

    def reboot(self, device_id):
        """Dispatch reboot device request to ACS."""
        data = {"name": "reboot"}
        return self.dispatch_device_task(device_id, data)

    def refresh_object(self, device_id):
        """Dispatch refreshObject request for the device to ACS."""
        data = {"name": "refreshObject", "objectName": ""}
        return self.dispatch_device_task(device_id, data)

    def delete_device(self, device_id):
        """Dispatch delete device to delete it from mongodb."""
        req = build_request(
            url=self.devices_url(device_id),
            method="DELETE")
        return self.perform_request(req)

    def perform_request(self, request):
        """Execute request and return response content."""
        opener = urllib.request.build_opener(
            urllib.request.HTTPHandler(debuglevel=1 if self.verbose else 0)
        )
        response = opener.open(request, timeout=self.timeout)
        return response.read()
