import argparse
import logging
import os
import re
import time

import helpers
import sandbox.core as sand
import usb.core


logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def main():
    path = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(usage="%(prog)s [options]")

    parser.add_argument("--verbose", "-v",
                        action="store_true",
                        default=False,
                        help="Display verbose information"
                        )

    parser.add_argument("--restore", "-r",
                        action="store_true",
                        default=False,
                        help="Restore system to its original state (bringing network interfaces back up \
                        removing usb device from allowed usbguard list)"
                        )

    parser.add_argument("--sandbox", "-s",
                        type=str,
                        action="store",
                        required=True,
                        help="Specify the name or uuid of your virtual box"
                        )

    args = parser.parse_args()
    verbose = args.verbose
    restore = args.restore
    sandbox_id = args.sandbox

    # check if usbguard is installed
    if not usb.core.USBGuard.check_if_installed():
        logger.error(f"\n\nPlease download and install usbguard from https://github.com/USBGuard/usbguard\n\n")
        raise SystemExit

    usb_objects = list()

    # while no usb device is attached
    while len(usb_objects) <= 0:
        usb_devices = helpers.lookup_usb_devices()
        if verbose:
            logger.debug(usb_devices)

        key_list = list()
        [key_list.append(k) for k, v in usb_devices.items() for i in v if i.find("MassStorage") != -1]

        usb_objects = [usb.core.USB(device_id=usb_devices[k][0],
                                    vendor_id=usb_devices[k][1],
                                    product_id=usb_devices[k][2],
                                    serial=usb_devices[k][3]) for k in key_list]

        if verbose:
            for obj in usb_objects:
                logger.debug(obj.vendor_id)
                logger.debug(obj.product_id)
                logger.debug(obj.device_id)
                logger.debug(obj.serial)

        print("\n\nWaiting for usb mass storage device to connect...\n\n")
        time.sleep(5)

    network_interfaces = helpers.get_network_interfaces()
    try:
        network_interfaces.remove("lo")
        network_interfaces = [x for x in network_interfaces if not x.startswith("docker")]
    except ValueError:
        logger.error("Couldn't ignore loopback interface - interface not found.")
        pass

    print(f"\n\nFound {len(network_interfaces)} network interfaces: {network_interfaces}")
    print("Disconnecting interfaces...")
    # for interface in network_interfaces:
        # core.USB.disconnect_network_interfaces(interface)

    if verbose:
        logger.debug(f"Sandbox ID/name given: {sandbox_id}")

    if re.match("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", str(sandbox_id)):
        sandbox = sand.Sandbox(uuid=sandbox_id, device_ids=[x.device_id for x in usb_objects])
    else:
        sandbox = sand.Sandbox(name=sandbox_id, device_ids=[x.device_id for x in usb_objects])

    # Before running VirtualBox check if current user is in the vboxuser group in order to use USB devices
    if not helpers.check_user_is_in_vboxgroup():
        logger.error(f"Please add your user to the vboxuser group using the following command: \n\n"
              f"sudo usermod -a -G vboxusers $USER\n\n")
        raise SystemExit

    if verbose:
        logging.debug("Name: ", sandbox.name)
        logging.debug("UUID: ", sandbox.uuid)

    sandbox.run_sandbox()

    usb_uuids = helpers.get_usb_uuid(usb_objects)

    if verbose:
        print("Looked up USB uuids from device_id: ", usb_uuids)

    sandbox.mount_usb_to_sandbox(usb_uuids)
    print(f"Successfully mounted {sandbox.sandbox_id}.")

    # If Sandbox VM is closed before USB device gets removed -> block device on host using usbguard to avoid automount
    while helpers.is_vm_running(sandbox.sandbox_id):
        print(f"VM {sandbox.sandbox_id} is still up and running.")
        time.sleep(1)

    usbguard = usb.core.USBGuard(device_ids=[x.device_id for x in usb_objects])
    usbguard.block_device()


if __name__ == '__main__':
    main()