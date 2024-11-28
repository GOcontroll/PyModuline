import json
import subprocess

from services import get_service, set_service


def get_wifi() -> bool:
    return get_service("go-wifi")


def set_wifi(enable: bool) -> "tuple[bool, str]":
    """
    Returns a tuple where bool is false if the service failed to change
    and str contains errors.
    """
    return set_service("go-wifi", enable)


def get_wifi_address() -> str:
    out = subprocess.run(
        ["ip", "-j", "address"], stdout=subprocess.PIPE, text=True, check=True
    )
    interfaces = json.loads(out.stdout)
    for interface in interfaces:
        if interface["ifname"] == "wlan0":
            return interface["addr_info"][0]["local"]
    else:
        return "no address"


def get_ap_address():
    out = subprocess.run(
        ["nmcli", "-t", "con", "show", "GOcontroll-AP"],
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    )
    lines = out.stdout.splitlines()
    for line in lines:
        if line.startswith("ipv4.addresses:"):
            return line.removeprefix("ipv4.addresses:").split("/")[0]
    pass


def set_ap_address(str):
    subprocess.run(
        ["nmcli", "con", "mod", "GOcontroll-AP", "ipv4.addresses", f"{str}/16"],
        check=True,
    )
