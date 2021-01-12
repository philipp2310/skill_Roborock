from core.device.model.Device import Device
from core.myHome.model.Location import Location
from core.device.model.DeviceType import DeviceType
from core.device.model.DeviceLink import DeviceLink
from core.commons import constants
import sqlite3
import threading
import socket
from core.base.model.ProjectAliceObject import ProjectAliceObject
from core.dialog.model.DialogSession import DialogSession
from core.device.model.DeviceException import RequiresGuiSettings
from miio import Vacuum
from typing import List, Union, Dict


class RoborockS5(DeviceType):

	LOC_SETTINGS = { 'roomId': '' }

	def __init__(self, data: Union[sqlite3.Row, Dict]):
		super().__init__(data)


	def discover(self, device: Device, uid: str, replyOnSiteId: str = "", session:DialogSession = None) -> bool:
		self.logInfo(f'searching for a roborock')
		if not 'ip' in device.devSettings or not 'token' in device.devSettings:
			device.changedDevSettingsStructure(self.DEV_SETTINGS)
		ip = device.devSettings['ip']
		token = device.devSettings['token']

		# check device settings for ip and token -> end dialog: Please supply informaition via interface
		if not ip or not token:
			raise RequiresGuiSettings()

		# check settings by sending a command(Hello?)
		vac = self.getVac(device=device)
		serial = vac.serial_number()
		vac.find()
		# connected?
		device.pairingDone(uid=serial)
		return True


	#required by every vacuum
	def clean(self, device: Device, links: List[DeviceLink]):
		if not isinstance(links, List): links = [links]

		vac = self.getVac(device=device)
		roomIds = [int(l.locSettings['roomId']) for l in links]

		if device.devSettings['enableQueue'] == "X":
			#todo get device Status - if cleaning, add to buffer and return to prevent overwrite!
			pass

		vac.segment_clean(roomIds)

	#required by every vacuum
	def charge(self, device: Device):
		vac = self.getVac(device=device)
		vac.send("app_charge")


	#required by every vacuum
	def locate(self, device: Device):
		vac = self.getVac(device=device)
		vac.find()


	def getVac(self, device:Device) -> Vacuum:
		# token has to be taken from emulator, backup or similar
		return Vacuum(device.devSettings['ip'], device.devSettings['token'])


	def getDeviceIcon(self, device: Device) -> str:
		#todo figure out a concept getting the current state of the vac
		return 'RoborockS5.png'


	def toggle(self, device: Device):
		self.getVac(device=device).find()
