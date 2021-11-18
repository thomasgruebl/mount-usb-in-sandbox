import logging
import os
import pickle

import usb.core

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def restore_changes():
    """
    Brings network interfaces back up (that have previously been disabled) and block usb devices
    that have been allowed with usbguard.
    """
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
            logger.debug(f"\n\nReconnecting to {i} interface...")
            usb.core.USB.connect_disconnect_network_interfaces("connect", i)

        # block usb device using usbguard
        usbguard = usb.core.USBGuard(device_ids=allowed_usbguard)
        if usbguard.check_if_installed():
            usbguard.block_device()
    except:
        logger.error("Could not properly restore changes from at least one log files.")
    else:
        logger.debug("Restored changes from log files [interfaces.pickle] and/or [allowed_usbguard.pickle]")

        # delete restore files
        os.remove('interfaces.pickle')
        os.remove('allowed_usbguard.pickle')

