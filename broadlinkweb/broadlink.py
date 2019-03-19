from base64 import b64decode, b64encode
from broadlinkweb import exceptions
import broadlink
import struct
import json
import time
import os

class Broadlink():

    #Timeout in seconds for learning mode
    TIMEOUT = 15
    DEVICES_FILE = os.path.dirname(os.path.realpath(__file__)) + '/devices/devices.json'

    def getDevices(self):
        with open(self.DEVICES_FILE) as json_file:  
            devices = json.load(json_file)
        if not devices:
            self.searchDevices()
            with open(self.DEVICES_FILE) as json_file:  
                devices = json.load(json_file)
        return devices

    def searchDevices(self):
        #Open existing devices
        with open(self.DEVICES_FILE) as json_file:  
            devices = json.load(json_file)

        #Get devices in network
        newDevices = broadlink.discover(timeout=5)
        for newDevice in newDevices:
            raw_mac = struct.unpack("BBBBBB", newDevice.mac)
            mac = "%02x:%02x:%02x:%02x:%02x:%02x" % raw_mac
            deviceName = str(newDevice.type) + '(' + mac + ')'
            host, port = newDevice.host
            devices[deviceName] = {
                'host': host,
                'port': port,
                'mac': mac,
                'devtype': newDevice.devtype,
                'type': newDevice.type,
                'raw_mac': raw_mac,
                'commands': {}
            }
        self.saveDevices(devices)

    def learn(self, deviceName, command):
        if deviceName is None:
            raise exceptions.AppException("Please select a device")
        devices = self.getDevices()
        if command in devices[deviceName]['commands']:
            raise exceptions.AppException("Command already exists")
        device = self.getDeviceByName(deviceName)
        self.connectToDevice(device)
        try:
            device.enter_learning()
        except Exception:
            raise exceptions.AppException("Unable to enter learning mode")
        
        packet = None
        start = time.time()
        while packet == None:
            packet = device.check_data()
            if (time.time() - start) > self.TIMEOUT:
                raise exceptions.AppException("Learning timed out")
        self.addCommandToDevice(deviceName, command, format(b64encode(packet).decode('utf8')))

    def send(self, deviceName, command):
        device = self.getDeviceByName(deviceName)
        self.connectToDevice(device)
        commandData = self.getCommandByName(deviceName, command)
        packet =commandData['packet']
        extra = len(packet) % 4
        if extra > 0:
            packet = packet + ('=' * (4 - extra))
        payload = b64decode(packet)
        try:
            device.send_data(payload)
        except Exception:
            raise exceptions.AppException("Unable to send command")

    def connectToDevice(self, device):
        try:
            device.auth()
        except Exception:
            raise exceptions.AppException("Unable to connect to device")

    def addCommandToDevice(self, deviceName, command, packet):
        devices = self.getDevices()
        devices[deviceName]['commands'][command] = {
            'packet': packet
        }
        self.saveDevices(devices)

    def getCommandByName(self, deviceName, command):
        devices = self.getDevices()
        return devices[deviceName]['commands'][command]

    def getDeviceByName(self, name):
        devices = self.getDevices()
        device = devices[name]
        return broadlink.gendevice(device['devtype'], (device['host'], device['port']), bytearray(device['raw_mac']))

    def deleteCommand(self, deviceName, command):
        devices = self.getDevices()
        devices[deviceName]['commands'].pop(command, None)
        self.saveDevices(devices)
    
    def deleteDevice(self, deviceName):
        devices = self.getDevices()
        devices.pop(deviceName, None)
        self.saveDevices(devices)

    def saveDevices(self, devices):
        with open(self.DEVICES_FILE, 'w') as outfile:  
            json.dump(devices, outfile)