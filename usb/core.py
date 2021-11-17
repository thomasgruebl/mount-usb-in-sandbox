import subprocess
import getpass
import logging
import pickle
import sys

from typing import List, Any

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class SudoError(Exception):
    pass


class USB:

    def __init__(self, device_id, vendor_id, product_id, serial):
        self.device_id = device_id
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.serial = serial

    @staticmethod
    def __prompt_sudo() -> Any:
        """
        Prompts sudo password in command line.

        :return: Returns a prompt request object
        :rtype: Any
        """
        return getpass.getpass(prompt='\n\nPLEASE ENTER YOUR SUDO PASSWORD: ')

    @staticmethod
    def connect_disconnect_network_interfaces(action: str, interface: str):
        """
        Connects or disconnects network interface.

        :param action: Connect or disconnect
        :type action: str
        :param interface: Network interface name
        :type interface: str
        """
        __sudo_pw = USB.__prompt_sudo()
        if action == "connect":
            command = "sudo -S ifconfig " + interface + " up"
        elif action == "disconnect":
            command = "sudo -S ifconfig " + interface + " down"
        else:
            logger.error("Cannot connect or disconnect network interface")
            return

        p = subprocess.Popen(command,
                             shell=True,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE)
        try:
            stdout, stderr = p.communicate(input=(__sudo_pw + '\n').encode(), timeout=5)
            logger.debug(f"{stdout}, {stderr}")
            stderr = stderr.decode('UTF-8')

            if (stderr.find("no password was provided") != -1) or (stderr.find("incorrect password") != -1):
                raise SudoError(stderr)
        except SudoError:
            logger.error(SudoError)
            sys.exit(1)


class USBGuard:

    def __init__(self, device_ids: List[str]):
        self.device_ids = device_ids

    @staticmethod
    def check_if_installed() -> bool:
        """
        Checks if usbguard is installed.

        :return: Returns true if installed, else false
        :rtype: bool
        """
        p = subprocess.Popen(["which", "usbguard"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        stdout = stdout.decode('UTF-8').splitlines()
        stderr = stderr.decode('UTF-8').splitlines()
        logger.debug(f"{stdout}, {stderr}")

        if len(stdout) <= 0:
            return False
        return True

    @staticmethod
    def allow_device():
        """
        Allows usb devices that have been blocked by usbguard
        """
        def __list_devices() -> List[str]:
            """
            Private inner function that lists all usb devices.

            :return: Returns a list of blocked usb device IDs
            :rtype: List[str]
            """
            try:
                list_devices = subprocess.Popen(["usbguard", "list-devices"],
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                blocked_usbs = subprocess.check_output(["grep",
                                                        "-E",
                                                        "[0-9]{1,2}: block id"],
                                                       stdin=list_devices.stdout)
            except subprocess.CalledProcessError:
                blocked_usbs = []

            if len(blocked_usbs) > 0:
                blocked_usbs = blocked_usbs.decode('UTF-8').splitlines()
                blocked_usbs = [x[:2] for x in blocked_usbs]
                return blocked_usbs
            else:
                return []

        usbs = __list_devices()
        logger.debug(f"USBGUARD IDs of blocked usb devices: {usbs}")
        for usb in usbs:
            allow_device = subprocess.Popen(["usbguard", "allow-device", usb],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = allow_device.communicate()
            logger.debug(f"{stdout}, {stderr}")

        # make changes persistent and note them in the pickle logfile (to be able to --restore)
        with open('allowed_usbguard.pickle', 'ab') as f:
            pickle.dump(usbs, f, pickle.HIGHEST_PROTOCOL)

    def block_device(self):
        """
        Blocks a usb device using the 'usbguard block-device' command.

        :param self: the sandbox_id is either the name or the uuid of the box, depending on the user's input
        :type self: USBGuard
        """
        def __find_device_id() -> List[str]:
            """
            Lookup usbguard device ID.

            :return: Returns list of device IDs
            :rtype: List[str]
            """
            d = list()
            try:
                list_devices = subprocess.Popen(["usbguard", "list-devices"],
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                for device_id in self.device_ids:
                    matched_usbs = subprocess.check_output(["grep",
                                                            "-E",
                                                            device_id],
                                                           stdin=list_devices.stdout)
                    matched_usbs = matched_usbs.decode('UTF-8').splitlines()
                    d.append(matched_usbs[0].split(":")[0])
            except subprocess.CalledProcessError:
                d = []

            return d

        devices = __find_device_id()
        for device in devices:
            block_device = subprocess.Popen(["usbguard", "block-device", device],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = block_device.communicate()
            logger.debug(f"{stdout}, {stderr}")


