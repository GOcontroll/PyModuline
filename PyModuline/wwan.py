import json
import subprocess

import PyModuline.services as services


def get_wwan() -> bool:
    return services.get_service("go-wwan")


def set_wwan(new_state: bool) -> tuple[bool, str]:
    return services.set_service("go-wwan", new_state)


def get_sim_num() -> dict:
    sim_command_res = subprocess.run(
        ["mmcli", "-i", "0", "-J"], stdout=subprocess.PIPE, text=True, check=True
    ).stdout
    return json.loads(sim_command_res)["sim"]["properties"]["iccid"]


def get_wwan_stats() -> dict:
    modem = subprocess.run(
        ["mmcli", "-J", "--list-modems"], stdout=subprocess.PIPE, text=True, check=True
    )
    modem = json.loads(modem.stdout)
    modem_number = modem["modem-list"][0]
    output = subprocess.run(
        ["mmcli", "-J", "--modem=" + modem_number],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    mmcli = json.loads(output.stdout)
    stats = {}
    stats["imei"] = mmcli["modem"]["3gpp"]["imei"]
    stats["operator"] = mmcli["modem"]["3gpp"]["operator-name"]
    stats["model"] = mmcli["modem"]["generic"]["model"]
    stats["signal"] = mmcli["modem"]["generic"]["signal-quality"]["value"]
    return json.dumps(stats)


def get_apn() -> dict:
    out = subprocess.run(
        ["nmcli", "con", "show", "GO-cellular"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    lines = out.stdout.splitlines()
    for line in lines:
        if line.startswith("gsm.apn:"):
            return line.removeprefix("gsm.apn:")
    else:
        return "no address"


def set_apn(apn: str):
    subprocess.run(["nmcli", "con", "mod", "GO-cellular", "gsm.apn", apn], check=True)


def set_pin(pin: str):
    subprocess.run(["nmcli", "con", "mod", "GO-cellular", "gsm.pin", pin], check=True)
