from datetime import datetime
from enum import Enum


class SystemMode(Enum):
    Zeitgesteuert = "Zeitgesteuert"
    Kellermode = "Kellermode"
    Behaglichkeitsmode = "Behaglichkeitsmode"


def _to_float(x: str):
    if x == "N/A":
        return None
    return float(x.replace(",", "."))


def _to_bool(x: str):
    return x == "1"


_CONVERSION_DICT = {
    "Date": lambda x: datetime.strptime(x, "%d.%m.%Y").date(),
    "Time": lambda x: datetime.strptime(x, "%H:%M:%S").time(),
    # "MAC": lambda x: hex(int(x, 16)),
    "RSSI": int,
    "SystemMode": lambda x: SystemMode(x),
    "Speed_In": int,
    "Speed_Out": int,
    "Speed_AntiFreeze": int,
    "Temp_In": _to_float,
    "Temp_Out": _to_float,
    "Temp_Fresh": _to_float,
    "rel_Humidity_In": _to_float,
    "rel_Humidity_Out": _to_float,
    "abs_Humidity_In": _to_float,
    "abs_Humidity_Out": _to_float,
    "Efficiency": _to_float,
    "Humidity_Transport": int,
    "SystemOn": _to_bool,
    "FrostschutzAktiv": _to_bool,
    "SpeedFrozen": _to_bool,
    "AbtauMode": _to_bool,
    "TimerActiv": _to_bool,
    "VermieterMode": _to_bool,
    "QuerlueftungAktiv": _to_bool,
}


def convert(key: str, value: str):
    try:
        return _CONVERSION_DICT.get(key, str)(value)
    except ValueError:
        return None
