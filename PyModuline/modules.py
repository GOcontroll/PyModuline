import os
import subprocess


def get_modules() -> list[dict[str, str]]:
    with open("/usr/module-firmware/modules.txt", "r") as modules_file:
        raw_info = modules_file.read()
    lines = raw_info.splitlines()
    if len(lines) != 4:
        raise ValueError("modules.txt is invalid")
    modules = lines[0].split(":")
    manufacturers = lines[1].split(":")
    front_qrs = lines[2].split(":")
    back_qrs = lines[3].split(":")

    res = []

    for i, module in enumerate(modules):
        if module:
            res.append({"firmware": module})
            res[i]["manufacturer"] = manufacturers[i]
            res[i]["front_qr"] = front_qrs[i]
            res[i]["back_qr"] = back_qrs[i]
        else:
            res.append(None)
    return res


def scan_modules():
    subprocess.run(["go-modules", "scan"]).check_returncode()


def update_modules():
    subprocess.run(["go-modules", "update", "all"]).check_returncode()


def overwrite_module(slot: int, firmware: str):
    subprocess.run(["go-modules", "overwrite", str(slot), firmware]).check_returncode()


def get_firmwares() -> list[str]:
    firmwares = os.listdir("/usr/module-firmware")
    firmwares.remove("modules.txt")
    firmwares = [firmware.removesuffix(".srec") for firmware in firmwares]
    return firmwares
