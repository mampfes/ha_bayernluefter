# Bayernlüfter

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

This component adds support for [Bayernlüfter](https://www.bayernluft.de) devices to Home Assistant:

![Device](./doc/device.png)
![Fan](./doc/fan.png)

If you like this component, please give it a star on [github](https://github.com/mampfes/ha_bayernluefter).

This integration requires at least revision firmware revision WS32234601 (which supports JSON export).

## Installation

1. Ensure that [HACS](https://hacs.xyz) is installed.
2. Install **Bayernlüfter** integration via HACS.
3. Add **Bayernlüfter** integration to Home Assistant (one per device):

   [![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=bayernluefter)

In case you would like to install manually:

1. Copy the folder `custom_components/bayernluefter` to `custom_components` in your Home Assistant `config` folder.
2. Add **Bayernlüfter** integration to Home Assistant (one per device):

   [![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=bayernluefter)

## Device Name

By factory default, the device name is equal to the MAC address of the device. To set your own device name:

1. Open _WLAN Konfiguration_ of your device: `http://<ip-address/ipconfig.html`
2. In the box _Modulkonfiguration_ change the field `DeviceName`.
3. Click on _Speichern und neu starten_.

## Notes

Since firmware version WS32240427, the speed of the 3 fan motors can be controlled individually. But these controls will only work if the device is switched off!!! This is a limitation of the firmware of the device, not the integration.

## Acknowledgements

This component was inspired by <https://github.com/nielstron/ha_bayernluefter>.
