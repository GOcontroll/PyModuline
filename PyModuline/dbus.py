import gi
from pydbus import SystemBus

import PyModuline.nmconstants as nmconstants

gi.require_version("NM", "1.0")
from gi.repository import NM

NM_PATH = "org.freedesktop.NetworkManager"

global nm_client


def get_nm_client():
    global nm_client
    if nm_client is None:
        nm_client = NM.Client.new(None)
    return nm_client


def get_wifi_device():
    nm, bus = get_nm()
    devices = nm.GetDevices()

    for path in devices:
        dev = bus.get(NM_PATH, path)
        if dev.DeviceType == nmconstants.NM_DEVICE_TYPE_WIFI:
            return dev, bus, path
    else:
        raise EnvironmentError("No wifi device present")


def get_nm():
    bus = SystemBus()
    return bus.get(NM_PATH), bus
