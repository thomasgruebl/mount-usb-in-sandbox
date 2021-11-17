# mount-usb-in-sandbox

![GitHub last commit](https://img.shields.io/github/last-commit/thomasgruebl/mount-usb-in-sandbox?style=plastic) ![GitHub](https://img.shields.io/github/license/thomasgruebl/phone-scraper?style=plastic) <a style="text-decoration: none" href="https://github.com/thomasgruebl/mount-usb-in-sandbox/stargazers">
<img src="https://img.shields.io/github/stars/thomasgruebl/mount-usb-in-sandbox.svg?style=plastic" alt="Stars">
</a>
<a style="text-decoration: none" href="https://github.com/thomasgruebl/mount-usb-in-sandbox/fork">
<img src="https://img.shields.io/github/forks/thomasgruebl/mount-usb-in-sandbox.svg?style=plastic" alt="Forks">
</a>
<a style="text-decoration: none" href="https://github.com/thomasgruebl/mount-usb-in-sandbox/issues">
<img src="https://img.shields.io/github/issues/thomasgruebl/mount-usb-in-sandbox.svg?style=plastic" alt="Issues">
</a>

## Features
- Automatically mounts a USB device in a sandbox
- Rejects mount attempts on host using usbguard (https://usbguard.github.io/)
- Disconnects host from all network interfaces by default (optionally you can specify particular interfaces)
- Optionally mounts USB in a pre-configured Whonix sandbox (starts gateway + workstation)

## Dependencies
- VirtualBox (https://www.virtualbox.org/wiki/Downloads) including the VirtualBox Extension pack
- A VM image file e.g. Ubuntu 21.04 (https://releases.ubuntu.com/21.04/)
- Enable USB Controller in VirtualBox (Sandbox -> Settings -> USB)
- Download and install the latest usbguard release on your machine (https://github.com/USBGuard/usbguard/releases)
- Follow the usbguard installation instructions (https://usbguard.github.io/documentation/compilation.html)

You can display your VM UUID by running
```console
$ vboxmanage list vms
```

## Installation

```console
# clone the repo
$ git clone https://github.com/thomasgruebl/mount-usb-in-sandbox.git

# navigate into the repo
$ cd mount-usb-to-sandbox 

# install
$ pip3 install .
```

Alternatively, if pip installation does not work you can run the main:
```console
# run
$ python3 main.py [options]
```

## Usage

```console
$ mount-usb-in-sandbox --help
usage: mount-usb-in-sandbox [options]

required arguments:
  -s SANDBOX, --sandbox SANDBOX         Specify the name or uuid of your virtual box

optional arguments:
  -h, --help                            Show help information
  -v, --verbose                         Display verbose information
  -r, --restore                         Restore system to its original state (bringing network interfaces back up removing usb device from allowed usbguard list)
  -i INTERFACE, --interface INTERFACE   Specify interface names to disconnect from (space-seperated)
  -w, --whonix                          Specify the whonix flag to mount the USB device in your whonix workstation (needs whonix gateway as well)
  
```