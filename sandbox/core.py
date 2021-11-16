import subprocess
import usb.core
import logging

from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class Sandbox:
    def __init__(self, **kwargs):
        # TODO
        # add default values of vbox instead of "None" which are the name and uuid of the vbox image provided
        self.name = kwargs.get('name', None)
        self.uuid = kwargs.get('uuid', None)
        self.device_ids = kwargs.get('device_ids', None)

        if self.name is not None:
            self.sandbox_id = self.name
        else:
            self.sandbox_id = self.uuid

    def run_sandbox(self):
        s = subprocess.Popen(["vboxmanage", "startvm", self.sandbox_id],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = s.communicate()

    def mount_usb_to_sandbox(self, usb_uuid: List[str]):
        for uuid in usb_uuid:
            p = subprocess.Popen(["vboxmanage", "controlvm", self.sandbox_id, "usbattach", uuid],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            stdout = stdout.decode('UTF-8').splitlines()
            stderr = stderr.decode('UTF-8').splitlines()
            logger.debug(f"{stdout}, {stderr}")

        usbguard = usb.core.USBGuard(device_ids=self.device_ids)
        usbguard.allow_device()

        modifyvm = subprocess.Popen(
            ["vboxmanage", "modifyvm", self.sandbox_id, "--usbxhci", "on" "--usbohci", "on", "--usbehci", "on"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_modifyvm, stderr_modifyvm = modifyvm.communicate()
        stdout_modifyvm = stdout_modifyvm.decode('UTF-8').splitlines()
        stderr_modifyvm = stderr_modifyvm.decode('UTF-8').splitlines()
        logger.debug(f"{stdout_modifyvm}, {stderr_modifyvm}")

        usbfilter = subprocess.Popen(
            ["vboxmanage", "usbfilter", "add", "--target", self.sandbox_id, "--name", "allow_all_usbs"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_usbfilter, stderr_usbfilter = usbfilter.communicate()
        stdout_usbfilter = stdout_usbfilter.decode('UTF-8').splitlines()
        stderr_usbfilter = stderr_usbfilter.decode('UTF-8').splitlines()
        logger.debug(f"{stdout_usbfilter}, {stderr_usbfilter}")
