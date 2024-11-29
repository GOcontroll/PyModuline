import json
import subprocess

from PyModuline.services import get_service, set_service


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
    else:
        return "no address"


def set_ap_address(str):
    subprocess.run(
        ["nmcli", "con", "mod", "GOcontroll-AP", "ipv4.addresses", f"{str}/16"],
        check=True,
    )


def activate_ap():
    stdout = subprocess.run(
        ["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True, check=True
    )

    connections = stdout.stdout.rstrip().split("\n")
    wifi_connections = []
    for con in connections:
        if "wireless" in con:
            if "GOcontroll-AP" not in con:
                wifi_connections.append(con.split(":")[0])
    for con in wifi_connections:
        subprocess.run(
            ["nmcli", "con", "mod", con, "connection.autoconnect", "no"], check=True
        )

    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "GOcontroll-AP",
            "connection.autoconnect",
            "yes",
        ],
        check=True,
    )

    enable_connection("GOcontroll-AP")


def deactivate_ap():
    stdout = subprocess.run(
        ["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True, check=True
    )

    connections = stdout.stdout.rstrip().split("\n")
    wifi_connections = []
    for con in connections:
        if "wireless" in con:
            if "GOcontroll-AP" not in con:
                wifi_connections.append(con.split(":")[0])
    for con in wifi_connections:
        subprocess.run(
            ["nmcli", "con", "mod", con, "connection.autoconnect", "yes"], check=True
        )

        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "GOcontroll-AP",
                "connection.autoconnect",
                "no",
            ],
            check=True,
        )

        disable_connection("GOcontroll-AP")


def enable_connection(con: str):
    """Set the connection 'con' to up
    raises subprocess.CalledProcessError when unsuccessfull"""
    subprocess.run(["nmcli", "con", "up", con]).check_returncode()


def disable_connection(con: str):
    """Set the connection 'con' to down
    raises subprocess.CalledProcessError when unsuccessfull"""
    subprocess.run(["nmcli", "con", "down", con]).check_returncode()


def get_ap_status() -> bool:
    output = subprocess.run(
        ["nmcli", "-t", "con", "show", "GOcontroll-AP"],
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
        raise EnvironmentError("Could not find the autoconnect option in the AP info")


def set_ap_pass(new_password: str):
    if len(new_password) < 8:
        raise ValueError("New password must be at least 8 characters long")
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "GOcontroll-AP",
            "wifi-sec.psk",
            new_password,
        ],
        check=True,
    )


def set_ap_ssid(new_ssid: str):
    if len(new_ssid) < 1:
        raise ValueError("New ssid cannot be an empty string")
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "GOcontroll-AP",
            "802-11-wireless.ssid",
            new_ssid,
        ],
        check=True,
    )


def get_ap_connections() -> list[dict[str, str]]:
    """Get a list of hostnames connected to the access point\n
    Returns a list of dicts with 'mac', 'hostname' and 'ip' keys"""
    final_device_list = []
    stdout = subprocess.run(
        ["ip", "n", "show", "dev", "wlan0"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    connected_devices = stdout.stdout.split("\n")
    for i in reversed(range(len(connected_devices))):
        if (
            "REACHABLE" not in connected_devices[i]
            and "DELAY" not in connected_devices[i]
        ):
            connected_devices.pop(i)

    stdout = subprocess.run(
        ["cat", "/var/lib/misc/dnsmasq.leases"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    previous_connections = stdout.stdout.split("\n")[:-1]

    for connected_device in connected_devices:
        connected_device_list = connected_device.split(" ")
        for previous_connection in previous_connections:
            if connected_device_list[2] in previous_connection:
                final_device_list.append(
                    {
                        "mac": connected_device_list[2],
                        "hostname": previous_connection.split(" ")[3],
                        "ip": connected_device_list[0],
                    }
                )
    return final_device_list


def get_wifi_networks() -> list[dict[str, str]]:
    """Get the list of available wifi networks and their attributes"""
    if get_ap_status():
        raise EnvironmentError("The AP is still active, can't scan for wifi networks")

    # gets the list in a layout optimal for scripting, networks seperated by \n, columns seperated by :
    wifi_list = subprocess.run(
        ["nmcli", "-t", "dev", "wifi"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    known_conn_list = subprocess.run(
        ["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True, check=True
    )

    networks = wifi_list.stdout.rstrip().split("\n")
    networks_out = []
    for i in range(len(networks)):
        network = networks[i].split(":")
        if len(network) > 8:
            # some character that is not a space here means active
            connected = network[0] != " "
            # splitting by : unfortunately also splits the mac address, it also contains some \ characters
            # strip the \ characters and join it back
            mac = ":".join(map(lambda octet: octet.rstrip("\\"), network[1:7]))
            ssid = network[7]
            strength = network[11]
            security = network[13]
            networks_out.append(
                {
                    "connected": connected,
                    "mac": mac,
                    "ssid": ssid,
                    "strength": strength,
                    "security": security,
                    "known": known_conn_list.stdout.find(ssid) >= 0,
                }
            )
    return networks_out


def connect_to_wifi_network(ssid: str, password: str):
    known_conn_list = subprocess.run(
        ["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True, check=True
    )
    if known_conn_list.stdout.find(ssid) >= 0:
        subprocess.run(["nmcli", "con", "up", ssid], check=True)
        return
    result = subprocess.run(
        ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    # for some reason this function returns exit code 0 even on failure
    search_str = "Error:"
    idx = result.stdout.find(search_str)
    if idx >= 0:
        raise EnvironmentError(f"{result.stdout[len(search_str):].strip()}")


def delete_wifi_network(name: str):
    subprocess.run(["nmcli", "con", "delete", name], check=True)
