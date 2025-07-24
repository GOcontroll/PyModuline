import socket
import subprocess

import gi

import PyModuline.dbus as dbus
import PyModuline.networking as networking
import PyModuline.nmconstants as nmconstants

gi.require_version("NM", "1.0")
from gi.repository import NM, GLib


def get_wifi() -> bool:
    client = dbus.get_nm_client()
    return client.get_wireless_enabled() and client.wireless_hardware_get_enabled()


def get_wifi_mode() -> str:
    client = dbus.get_nm_client()
    wifi_device = client.get_device_by_iface("wlan0")
    if wifi_device is None:
        raise IOError("No WiFi device found")
    mode = wifi_device.get_mode()
    if mode == NM.SETTING_WIRELESS_MODE_INFRA:
        return "wifi"
    elif mode == NM.SETTING_WIRELESS_MODE_AP:
        return "ap"
    else:
        raise EnvironmentError(f"Wifi device in unexpected mode: {mode}")


def set_wifi(enable: bool):
    client = dbus.get_nm_client()
    client.dbus_set_property(
        NM.DBUS_PATH,
        NM.DBUS_INTERFACE,
        "WirelessEnabled",
        GLib.Variant("b", enable),
        -1,
        None,
        None,
        None,
    )


def get_wifi_address() -> str:
    client = dbus.get_nm_client()
    wifi_device = client.get_device_by_iface("wlan0")
    if wifi_device is None:
        raise IOError("No WiFi device found")
    config = wifi_device.get_ip4_config()
    addresses = config.get_addresses()
    if len(addresses):
        return addresses[0].get_address()
    raise EnvironmentError("WiFi device doesn't have an ipv4 address")


def get_ap_address() -> str:
    client = dbus.get_nm_client()
    ap_con = client.get_connection_by_id("GOcontroll-AP")
    settings = ap_con.get_setting_ip4_config()
    return settings.get_address(0)


def set_ap_address(ip: str):
    # TODO validate ip
    client = dbus.get_nm_client()
    ap_con = client.get_connection_by_id("GOcontroll-AP")
    settings = ap_con.get_setting_ip4_config()
    addr = settings.get_address(0)
    addr.set_address(ip)
    settings.clear_addresses()
    settings.add_address(addr)
    ap_con.commit_changes_async(True, None, None, None)


def activate_ap():
    client = dbus.get_nm_client()
    # this list of connections should not be modified
    connections = client.get_connections()
    for connection in connections:
        if connection.is_type(NM.SETTING_WIRELESS_SETTING_NAME):
            owned_connection = client.get_connection_by_uuid(connection.get_uuid())
            if owned_connection.get_id() == "GOcontroll-AP":
                owned_connection.get_setting_connection().set_property(
                    "autoconnect", "yes"
                )
                ap_connection = owned_connection
            else:
                owned_connection.get_setting_connection().set_property(
                    "autoconnect", "no"
                )
            owned_connection.commit_changes_async(True, None, None, None)
    client.activate_connection_async(ap_connection, None, None, None, None, None)


def deactivate_ap():
    client = dbus.get_nm_client()
    # this list of connections should not be modified
    connections = client.get_connections()
    for connection in connections:
        if connection.is_type(NM.SETTING_WIRELESS_SETTING_NAME):
            owned_connection = client.get_connection_by_uuid(connection.get_uuid())
            if owned_connection.get_id() == "GOcontroll-AP":
                owned_connection.get_setting_connection().set_property(
                    "autoconnect", "no"
                )
            else:
                owned_connection.get_setting_connection().set_property(
                    "autoconnect", "yes"
                )
            owned_connection.commit_changes_async(True, None, None, None)
    client.activate_connection_async(
        None, client.get_device_by_iface("wlan0"), None, None, None, None
    )


def set_ap_pass(new_password: str):
    if len(new_password) < 8:
        raise ValueError("New password must be at least 8 characters long")
    client = dbus.get_nm_client()
    ap_con = client.get_connection_by_id("GOcontroll-AP")
    settings = ap_con.get_setting_wireless_security()
    settings.set_property("psk", new_password)
    ap_con.commit_changes_async(True, None, None, None)


def set_ap_ssid(new_ssid: str):
    if len(new_ssid) < 1:
        raise ValueError("New ssid cannot be an empty string")
    client = dbus.get_nm_client()
    ap_con = client.get_connection_by_id("GOcontroll-AP")
    settings = ap_con.get_setting_wireless()
    settings.set_property("ssid", GLib.Bytes.new(bytearray(new_ssid, "utf-8")))
    ap_con.commit_changes_async(True, None, None, None)


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
    client = dbus.get_nm_client()
    wifi_device = client.get_device_by_iface("wlan0")

    wifi_device.RequestScan({})
    access_points = wifi_device.GetAccessPoints()
    active_point = wifi_device.ActiveAccessPoint()

    networks_out = []
    for ap_path in access_points:
        ap = bus.get(dbus.NM_PATH, ap_path)
        networks_out.append(
            {
                "connected": ap_path is active_point,
                "mac": bytearray(ap.HwAddress).decode("utf-8"),
                "ssid": bytearray(ap.Ssid).decode("utf-8"),
                "strength": str(ap.Strength),
                "security": "?",
            }
        )
    return networks_out


def connect_to_wifi_network(ssid: str, password: str):
    global connection_state
    connection_state = 0
    wifi_device, bus, wifi_path = dbus.get_wifi_device()
    nm, _ = dbus.get_nm()
    loop = GLib.MainLoop()

    def monitor_connection(new, old, reason):
        global connection_state
        # print(f"new {new}, old {old}, reason {reason}")
        if (
            new == nmconstants.NM_DEVICE_STATE_UNMANAGED
            or new == nmconstants.NM_DEVICE_STATE_ACTIVATED
            or new == nmconstants.NM_DEVICE_STATE_FAILED
        ):
            connection_state = new
            loop.quit()

    def check_timeout():
        loop.quit()

    try:
        _, con_path = networking.get_connection(ssid)
        wifi_device.onStateChanged = monitor_connection
        nm.ActivateConnection(con_path, "/", "/")
        GLib.timeout_add_seconds(60, check_timeout)
        loop.run()
        if connection_state == 0:
            raise TimeoutError("connection timed out")
        elif not connection_state == nmconstants.NM_DEVICE_STATE_ACTIVATED:
            raise ValueError(f"connection failed {connection_state}")
        else:
            return
    except EnvironmentError:
        pass

    settings = {
        "connection": {
            "id": GLib.Variant("s", ssid),
            "type": GLib.Variant("s", "802-11-wireless"),
        },
        "802-11-wireless": {
            "ssid": GLib.Variant("ay", bytearray(ssid, "utf-8")),
            "mode": GLib.Variant("s", "infrastructure"),
        },
        "802-11-wireless-security": {
            "key-mgmt": GLib.Variant("s", "wpa-psk"),
            "psk": GLib.Variant("s", password),
        },
        "ipv4": {"method": GLib.Variant("s", "auto")},
        "ipv6": {"method": GLib.Variant("s", "ignore")},
    }
    wifi_device.onStateChanged = monitor_connection
    nm.AddAndActivateConnection(settings, wifi_path, "/")
    GLib.timeout_add_seconds(60, check_timeout)
    # using threading.event it would not call monitor_connection
    loop.run()
    if connection_state == 0:
        raise TimeoutError("connection timed out")
    elif not connection_state == nmconstants.NM_DEVICE_STATE_ACTIVATED:
        raise ValueError(f"connection failed {connection_state}")
    else:
        return


def delete_wifi_network(name: str):
    client = dbus.get_nm_client()
    con = client.get_connection_by_id(name)
    con.delete_async(None, None, None)
