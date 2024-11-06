import subprocess
import time
from typing import Literal

import netifaces as ni

path = "/etc/NetworkManager/system-connections/Wired connection static.nmconnection"


def get_ethernet_mode() -> Literal["static", "dynamic"]:
    stdout = subprocess.run(
        ["nmcli", "con", "show", "--active"], stdout=subprocess.PIPE, text=True
    ).check_returncode()
    result = stdout.stdout
    result = result.split("\n")
    # active connection will be at the top of the list
    for name in result:
        if "Wired connection static" in name:
            if "eth0" in name:
                return "static"
        elif "Wired connection auto" in name:
            if "eth0" in name:
                return "dynamic"
        elif "Wired connection 1" in name:
            subprocess.run(
                [
                    "nmcli",
                    "con",
                    "mod",
                    "Wired connection 1",
                    "con-name",
                    "Wired connection auto",
                ]
            )
            if "eth0" in name:
                return "dynamic"
    else:
        raise FileNotFoundError


# get the information for the ethernet settings screen
def get_ethernet_settings():
    ret = {}
    ret["mode"] = get_ethernet_mode()
    try:
        ret["ip"] = ni.ifaddresses("eth0")[ni.AF_INET][0]["addr"]
    except:
        ret["ip"] = "no IP available"
    try:
        with open(path, "r") as con:
            ip_line = get_line(path, "address1=")
            file = con.readlines()
            ret["ip_static"] = file[ip_line].split("=")[1]
            ret["ip_static"] = ret["ip_static"].split("/")[0]
    except:
        subprocess.run(
            [
                "nmcli",
                "con",
                "add",
                "type",
                "ethernet",
                "con-name",
                "Wired connection static",
                "ifname",
                "eth0",
                "ipv4.addresses",
                "192.168.255.255/16",
                "ipv4.method",
                "manual",
                "connection.autoconnect",
                "no",
            ]
        )
        try:
            with open(path, "r") as con:
                ip_line = get_line(path, "address1=")
                file = con.readlines()
                ret["ip_static"] = file[ip_line].split("=")[1]
                ret["ip_static"] = ret["ip_static"].split("/")[0]
        except:
            ret["ip_static"] = "missing"
    return ret


# apply changes that were made by the user
def set_static_ethernet_ip(ip):
    subprocess.run(
        ["nmcli", "con", "mod", "Wired connection static", "ipv4.addresses", f"{ip}/16"]
    ).check_returncode()
    if get_ethernet_mode() == "static":
        subprocess.run(
            ["nmcli", "con", "up", "Wired connection auto"]
        ).check_returncode()
        time.sleep(0.5)
        subprocess.run(
            ["nmcli", "con", "up", "Wired connection static"]
        ).check_returncode()


# switch between static or dynamic ip connection
def set_ethernet_mode(mode: Literal["static", "dynamic"]):
    if mode == "static":
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection auto",
                "connection.autoconnect",
                "no",
            ]
        ).check_returncode()
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection static",
                "connection.autoconnect",
                "yes",
            ]
        ).check_returncode()
        subprocess.run(
            ["nmcli", "con", "up", "Wired connection static"]
        ).check_returncode()
    elif mode == "dynamic":
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection auto",
                "connection.autoconnect",
                "yes",
            ]
        ).check_returncode()
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection static",
                "connection.autoconnect",
                "no",
            ]
        ).check_returncode()
        subprocess.run(
            ["nmcli", "con", "up", "Wired connection auto"]
        ).check_returncode()
