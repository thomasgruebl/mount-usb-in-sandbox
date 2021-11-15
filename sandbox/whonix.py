from sandbox.core import Sandbox


class Whonix(Sandbox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def mount_usb_to_sandbox(self, usb_uuid: list[str]):
        # probably needs more sophisticated logic to mount usb (than parent method for "normal" VM)
        pass