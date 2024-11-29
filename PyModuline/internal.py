import json
import os
import subprocess

from PyModuline import services


def get_service(service: str) -> bool:
    if service not in services.get_service_blacklist() and service in services.services:
        return services.get_service(service)
    else:
        raise EnvironmentError("Service doesn't exist or is not allowed to be viewed")


def set_service(service: str, new_state: bool):
    if service not in services.get_service_blacklist() and service in services.services:
        is_changed, error = services.set_service(service, new_state)
        if is_changed:
            return new_state
        else:
            return json.dumps(
                {"err": f"Failed to change service '{service}' state {error}"}
            )
    else:
        raise EnvironmentError("Service doesn't exist or is not allowed to be set")


# simulink
def get_sim_ver() -> str:
    with open("/usr/mem-sim/MODEL_MAJOR", "r") as major:
        major_ver = major.readline()
    with open("/usr/mem-sim/MODEL_FEATURE", "r") as feature:
        feature_ver = feature.readline()
    with open("/usr/mem-sim/MODEL_FIX", "r") as fix:
        fix_ver = fix.readline()
    return f"V{major_ver}.{feature_ver}.{fix_ver}"


# controller info
def get_hardware():
    with open("/sys/firmware/devicetree/base/hardware", "r") as hardware_file:
        return hardware_file.read().strip()


def get_software():
    try:
        with open("/version.txt", "r") as file:
            return file.readline().strip()
    except FileNotFoundError:
        with open("/root/version.txt", "r") as file:
            return file.readline().strip()


def get_serial_number():
    res = subprocess.run(["go-sn", "r"], stdout=subprocess.PIPE, text=True, check=True)
    return res.stdout.strip()


def get_errors():
    # try to import a custom get_errors script
    try:
        import modulinedtc.errors as errors

        return errors.get_errors()
    # default route
    except ImportError:
        output = []
        files = os.listdir("/usr/mem-diag")
        for file in files:
            output.append({"fc": file})
        return output


def delete_errors(errors: list[str]):
    for file in errors:
        if ".." in file:
            continue
        os.remove(f"/usr/mem-diag/{file}")
