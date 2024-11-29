import json
import subprocess


def get_ethernet_static_status() -> bool:
    output = subprocess.run(
        ["nmcli", "-t", "con", "show", "Wired connection static"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    option = "connection.autoconnect:"
    idx = output.stdout.find(option)
    if idx >= 0:
        if output.stdout[idx + len(option)] == "y":
            return True
        else:
            return False
    else:
        raise EnvironmentError(
            "Could not find the autoconnect option in the Static connection info"
        )


def get_ethernet_address() -> str:
    out = subprocess.run(
        ["ip", "-j", "address"], stdout=subprocess.PIPE, text=True, check=True
    )
    interfaces = json.loads(out.stdout)
    for interface in interfaces:
        if interface["ifname"] == "eth0":
            return interface["addr_info"][0]["local"]
    else:
        return "no address"


def get_ethernet_static_address():
    out = subprocess.run(
        ["nmcli", "-t", "con", "show", "Wired connection static"],
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    )
    lines = out.stdout.splitlines()
    for line in lines:
        if line.startswith("ipv4.addresses:"):
            return line.removeprefix("ipv4.addresses:").split("/")[0]
    else:
        return "no address"


# apply changes that were made by the user
def set_static_ethernet_ip(ip):
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "Wired connection static",
            "ipv4.addresses",
            f"{ip}/16",
        ],
        check=True,
    )


# switch between static or dynamic ip connection
def activate_ethernet_static():
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "Wired connection auto",
            "connection.autoconnect",
            "no",
        ],
        check=True,
    )
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "Wired connection static",
            "connection.autoconnect",
            "yes",
        ],
        check=True,
    )
    subprocess.run(["nmcli", "con", "up", "Wired connection static"], check=True)


def deactivate_ethernet_static():
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "Wired connection auto",
            "connection.autoconnect",
            "yes",
        ],
        check=True,
    )
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "Wired connection static",
            "connection.autoconnect",
            "no",
        ],
        check=True,
    )
    subprocess.run(["nmcli", "con", "up", "Wired connection auto"], check=True)


# def get_static_ethernet_connections()?
