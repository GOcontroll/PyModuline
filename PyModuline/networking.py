import PyModuline.dbus as dbus


def connectivity_state() -> bool:
    nm, bus = dbus.get_nm()
    return (
        nm.Connectivity >= 4
    )  # https://people.freedesktop.org/~lkundrak/nm-docs/nm-dbus-types.html#NMConnectivityState
