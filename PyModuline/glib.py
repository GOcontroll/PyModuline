from gi.repository.GLib import Variant

VARIANTS = {
    "ssid": lambda v: Variant("ay", bytearray(v)),
    "apn": lambda v: Variant("s", v),
}


def variafy(key, value):
    return Variant()


def glibify(settings: dict) -> dict:
    for category_k, category_v in settings.items():
        for k, v in category_v.items():
            settings[category_k][k] = VARIANTS.get(k, lambda v: Variant("s", v))(v)
