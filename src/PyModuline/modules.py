def get_modules() -> list[dict[str, str]]:
    with open("/usr/module-firmware/modules.txt", "r") as modules_file:
        raw_info = modules_file.read()
    modules = raw_info.splitlines()[0].split(":")
    res = []

    for i, module in enumerate(modules):
        if module:
            pass

    pass


def scan_modules():
    # scan
    get_modules()
