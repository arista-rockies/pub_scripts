# Version 1.3
# Configlet Builder to search the CVP instance for transceivers containing a certain portion of a serial number
# Created by Allan Olsson | aolsson@arista.com

# XFH211xxxxxxx

import json
import ssl

from cvplibrary import CVPGlobalVariables, Form, GlobalVariableNames, RestClient

user = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_USERNAME)
passwd = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_PASSWORD)


def formatSerial(serial):
    serialStrip = serial.strip()
    serialUpper = serialStrip.upper()
    return serialUpper


def formatOutput(hostname, interface, serial):
    if 'Ethernet' in interface:
        intSplit = interface.split('net')
        port = intSplit[1]
    else:
        port = interface

    hnSpace = 25 - len(hostname)
    intSpace = 10 - len(port)
    print('{}{}{}{}{}'.format(hostname, ' ' * hnSpace, port, ' ' * intSpace, serial))


def queryCVP(url):
    method = 'GET'
    client = RestClient(url, method)
    if client.connect():
        response = json.loads(client.getResponse())
    return response


def getHardwareInventory(device):  # Used for CVP 2021.3 and later
    deviceSN = queryCVP(
        'https://localhost/api/v1/rest/analytics/Devices/{}/versioned-data/hardware/inventory/xcvr'.format(
            device['serialNumber']
        )
    )

    for notification in deviceSN['notifications']:
        for interface in notification['updates']:
            for k, v in notification['updates'][interface]['value'].items():
                if k == 'serialNum':
                    if xcvrSerialInput in v:
                        formatOutput(device['hostname'], interface, v)
                    else:
                        continue
                else:
                    continue


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


print('HOSTNAME                 PORT      XCVR SERIAL')


devices = queryCVP('https://localhost/cvpservice/inventory/devices?provisioned=true')
xcvrSerialInput = formatSerial(Form.getFieldById('xcvrSerial').getValue())

for device in devices:
    getHardwareInventory(device)
