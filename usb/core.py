import subprocess
import getpass
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class USB:

    def __init__(self, device_id, vendor_id, product_id, serial):
        self.device_id = device_id
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.serial = serial

    @staticmethod
    def __prompt_sudo():
        return getpass.getpass(prompt='PLEASE ENTER YOUR SUDO PASSWORD: ')

    @staticmethod
    def disconnect_network_interfaces(interface: str):
        __sudo_pw = USB.__prompt_sudo()
        command = "sudo -S ifconfig " + interface + " down"
        p = subprocess.Popen(command,
                             shell=True,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE)
        try:
            stdout, stderr = p.communicate(input=(__sudo_pw + '\n').encode(), timeout=5)
            logger.debug(f"{stdout}, {stderr}")
        except subprocess.TimeoutExpired:
            p.kill()

        logger.info("Disconnecting network interfaces...")


class USBGuard:

    def __init__(self, device_ids: list[str]):
        self.device_ids = device_ids

    @staticmethod
    def check_if_installed() -> bool:
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
        def __list_devices() -> list[str | int]:
            try:
                list_devices = subprocess.Popen(["usbguard", "list-devices", ],
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

    def block_device(self):
        pass

