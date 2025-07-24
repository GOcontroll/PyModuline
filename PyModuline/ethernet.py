import json
import subprocess

import PyModuline.dbus as dbus


def get_ethernet_static_status() -> bool:
    client = dbus.get_nm_client()
    con = client.get_connection_by_id("Wired connection static")
    return con.get_setting_connection().get_property("autoconnect")


def get_ethernet_ip() -> str:
    client = dbus.get_nm_client()
    eth_device = client.get_device_by_iface("end0")
    if eth_device is None:
        raise IOError("No eth device found")
    config = eth_device.get_ip4_config()
    addresses = config.get_addresses()
    if len(addresses):
        return addresses[0].get_address()
    raise EnvironmentError("eth device doesn't have an ipv4 address")


def get_ethernet_static_ip():
    client = dbus.get_nm_client()
    static_con = client.get_connection_by_id("Wired connection static")
    settings = static_con.get_setting_ip4_config()
    return settings.get_address(0)


def set_static_ethernet_ip(ip):
    # TODO validate ip
    client = dbus.get_nm_client()
    eth_con = client.get_connection_by_id("Wired connection static")
    settings = eth_con.get_setting_ip4_config()
    addr = settings.get_address(0)
    addr.set_address(ip)
    settings.clear_addresses()
    settings.add_address(addr)
    eth_con.commit_changes_async(True, None, None, None)


# switch between static or dynamic ip connection
def activate_ethernet_static():
    client = dbus.get_nm_client()
    con_static = client.get_connection_by_id("Wired connection static")
    con_auto = client.get_connection_by_id("Wired connection auto")
    static_settings = con_static.get_setting_connection()
    auto_settings = con_auto.get_setting_connection()
    static_settings.set_property("autoconnect", True)
    auto_settings.set_property("autoconnect", False)
    con_static.commit_changes_async(True, None, None, None)
    con_auto.commit_changes_async(True, None, None, None)
    client.activate_connection_async(con_static, None, None, None, None, None)


def deactivate_ethernet_static():
    client = dbus.get_nm_client()
    con_static = client.get_connection_by_id("Wired connection static")
    con_auto = client.get_connection_by_id("Wired connection auto")
    static_settings = con_static.get_setting_connection()
    auto_settings = con_auto.get_setting_connection()
    static_settings.set_property("autoconnect", False)
    auto_settings.set_property("autoconnect", True)
    con_static.commit_changes_async(True, None, None, None)
    con_auto.commit_changes_async(True, None, None, None)
    client.activate_connection_async(con_auto, None, None, None, None, None)


# def get_static_ethernet_connections()?
