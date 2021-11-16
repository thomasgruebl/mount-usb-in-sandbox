from sandbox.core import Sandbox
from typing import List


class Whonix(Sandbox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def mount_usb_to_sandbox(self, usb_uuid: List[str]):
        # probably needs more sophisticated logic to mount usb (than parent method for "normal" VM)
        pass