# TODO hash password


def set_bluetooth_password(new_password: str):
    with open("/etc/bluetooth/trusted_devices.txt", "r") as bluetooth_conf:
        lines = bluetooth_conf.readlines()
        lines[0] = new_password
    with open("/etc/bluetooth/trusted_devices.txt", "w") as bluetooth_conf:
        bluetooth_conf.write("\n".join(lines))


def set_bluetooth_name(new_name: str):
    # name must contain GOcontroll otherwise the app will not show it
    if new_name.find("GOcontroll") < 0:
        new_name = f"GOcontroll-{new_name}"
    with open("/etc/machine-info", "r") as machine_info:
        lines = machine_info.readlines()
        for line in lines:
            if line.startswith("PRETTY_HOSTNAME"):
                line = f"PRETTY_HOSTNAME={new_name}"


def reset_bluetooth_trusted_devices():
    with open("/etc/bluetooth/trusted_devices.txt", "r") as bluetooth_conf:
        lines = bluetooth_conf.readlines()
        new_contents = f"{lines[0]}\n"
    with open("/etc/bluetooth/trusted_devices.txt", "w") as bluetooth_conf:
        bluetooth_conf.write(new_contents)


def reset_bluetooth_password():
    with open("/sys/class/net/eth0/address", "r") as default_password_file:
        new_password = default_password_file.read()
    set_bluetooth_password(new_password)
