import pickle
import usb.core
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def restore_changes():
    try:
        with open('interfaces.pickle', 'rb') as f:
            ints = pickle.load(f)

        with open('allowed_usbguard.pickle', 'rb') as f:
            allowed_usbguard = pickle.load(f)
    except FileNotFoundError:
        logger.error("At least one restore file is missing.")

    try:
        # reconnect network interfaces that have previously been disconnected
        for i in ints:
            usb.core.USB.connect_disconnect_network_interfaces("connect", i)
            logger.debug(f"Reconnecting to {interface} interface...")

        # block usb device using usbguard
        usbguard = usb.core.USBGuard(device_ids=allowed_usbguard)
        if usbguard.check_if_installed():
            usbguard.block_device()
    except:
        pass

    logger.debug("Restored changes from log files [interfaces.pickle] and/or [allowed_usbguard.pickle]")
