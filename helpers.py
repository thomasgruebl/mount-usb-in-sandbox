import subprocess
import re
from typing import DefaultDict, List
from collections import defaultdict
from usb.core import USB


## TODO:


## add whonix functionality


def check_user_is_in_vboxgroup() -> bool:
    """
    Check if current user is in vboxgroup.

    :return: True if user is in vboxgroup, else False
    :rtype: bool
    """
    groups = subprocess.Popen(["groups"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = groups.communicate()
    groups = stdout.decode('UTF-8').splitlines()

    for group in groups:
        if group.find("vboxusers") != -1:
            return True

    return False


def get_network_interfaces() -> List[str]:
    """
    Returns a list of network interfaces.

    The list of network interfaces is later used to shut down the interfaces

    :return: list of network interfaces
    :rtype: list[str]
    """
    ints = subprocess.Popen(["ip", "link", "show"], stdout=subprocess.PIPE)
    ints = subprocess.check_output(["grep",
                                    "-oE", "[0-9]{1,2}:.*: <"], stdin=ints.stdout)
    ints = ints.decode('UTF-8').splitlines()
    ints = [re.search(": (.*):", x).group(1) for x in ints]

    return ints


def is_vm_running(sandbox_id: str) -> bool:
    """
    Checks if a the sandbox VM is still up and running.

    :param sandbox_id: the sandbox_id is either the name or the uuid of the box, depending on the user's input
    :type sandbox_id: str
    :return: Returns True if VM is running, else False
    :rtype: bool
    """
    running_vms = subprocess.Popen(["vboxmanage", "list", "runningvms"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = running_vms.communicate()
    running_vms = stdout.decode('UTF-8').splitlines()

    running_vms = [re.search("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", x).group(0)
                   for x in running_vms]

    for uuid in running_vms:
        if uuid == sandbox_id:
            return True

    return False


def get_usb_uuid(usb_objects: List[USB]) -> List[str]:
    """
    Finds UUID of USB mass storage based on the device_id stored in the USB objects.

    :param usb_objects: List of USB objects
    :type usb_objects: list[USB]
    :return: List of UUIDS of all attached USB mass storages
    :rtype: list[str]
    """
    usb_uuids = list()

    usbhosts = subprocess.Popen(["vboxmanage", "list", "usbhost"], stdout=subprocess.PIPE)
    usbhosts = subprocess.check_output(["grep",
                                        "-e", "UUID: ",
                                        "-e", "VendorId: ",
                                        "-e", "ProductId: "], stdin=usbhosts.stdout)
    usbhosts = usbhosts.decode('UTF-8').splitlines()
    usbhosts = [x.replace(" ", "") for x in usbhosts]

    temp = list()
    [temp.append(usbhosts[i] + usbhosts[i + 1] + usbhosts[i + 2]) \
     for i in range(0, len(usbhosts)) if usbhosts[i].find('UUID:') != -1]

    temp_dict = defaultdict(str)
    for x in temp:
        uuid = re.search("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", x).group(0)
        vendor_id = re.search("(?<=VendorId:0x)[0-9a-f]{4}", x).group(0)
        product_id = re.search("(?<=ProductId:0x)[0-9a-f]{4}", x).group(0)

        device_id = vendor_id + ":" + product_id
        temp_dict[uuid] = device_id

    # lookup uuids from device_id  (e.g. 8087:0026 -> e0c6ec26-4ad1-4d55-97c8-f0f35c538e95)
    [usb_uuids.append(k) for k, v in temp_dict.items() for obj in usb_objects if obj.device_id == v]

    return usb_uuids


def lookup_usb_devices() -> DefaultDict[int, list]:
    """
    Query available USB devices that are listed in the "lsusb" command

    :return: Returns a dict with an index (key) and USB device information (value) such as device_id, vendor_id,
                product_id, serial_number, interface_class
    :rtype: DefaultDict[int, list]
    """
    grep_keywords = ['idVendor', 'idProduct', 'iSerial', 'bInterfaceClass']
    device_id = subprocess.Popen("lsusb", stdout=subprocess.PIPE)
    device_id = subprocess.check_output(["grep",
                                         "-oE", "ID [a-f0-9]{4}:[a-f0-9]{4}"], stdin=device_id.stdout)
    lsusb_verbose = subprocess.Popen(["lsusb", "-v", ], stdout=subprocess.PIPE)
    lsusb_verbose = subprocess.check_output(["grep",
                                             "-e", grep_keywords[0],
                                             "-e", grep_keywords[1],
                                             "-e", grep_keywords[2],
                                             "-e", grep_keywords[3]], stdin=lsusb_verbose.stdout)

    device_id = device_id.decode('UTF-8').splitlines()
    device_id = [str(x).replace("ID ", "") for x in device_id]

    lsusb_verbose = lsusb_verbose.decode('UTF-8').splitlines()
    lsusb_verbose = [str(x).replace(" ", "") for x in lsusb_verbose]

    usb_devices = defaultdict(list)
    idx = -1
    for x in lsusb_verbose:
        if x.find('idVendor') != -1:
            idx = idx + 1
            usb_devices[idx].append(device_id[idx])
        usb_devices[idx].append(x)

    # remove duplicates
    for k, v in usb_devices.items():
        usb_devices[k] = list(dict.fromkeys(v))

    return usb_devices
