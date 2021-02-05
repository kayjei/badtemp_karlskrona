"""
A sensor created to read temperature from swimareas in Karlskrona Sweden
For more details about this platform, please refer to the documentation at
https://github.com/kayjei/swimareas_karlskrona
"""
import logging
import json
import urllib
import voluptuous as vol
import datetime
import secrets

from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.const import (TEMP_CELSIUS)
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

URL = 'https://service.karlskrona.se/FileStorageArea/Documents/bad/swimAreas.json'
PERS_JSON = '.badtemp_karlskrona.json'

UPDATE_INTERVAL = datetime.timedelta(minutes=3)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the sensor platform"""

    response = urllib.request.urlopen(URL)
    response_json = json.dumps(json.loads(response.read()))
    _LOGGER.debug("Response: " + response_json)
    with open(PERS_JSON, "w") as outfile:
        json.dump(response_json, outfile)

    dev = json.loads(response_json)

    devices = []

    poller_entity = dev["Payload"]["swimAreas"][0]["nameArea"].lower().replace("\xe5","a").replace("\xe4","a").replace("\xf6","o")
    _LOGGER.debug("Creating poller device: " + poller_entity)

    for jsonr in dev["Payload"]["swimAreas"]:
        _LOGGER.debug("Device: " + str(jsonr))
        name = str(jsonr["nameArea"]).capitalize()
        id = str.lower(name).replace("\xe5","a").replace("\xe4","a").replace("\xf6","o")
        temp = float(round(jsonr["temperatureWater"], 1))
        lat = str(jsonr["geometryArea"]["y"])
        lon = str(jsonr["geometryArea"]["x"])
        timestamp = datetime.datetime.strptime(str(jsonr["timeStamp"]).split('.')[0], "%Y-%m-%dT%H:%M:%S")

        if isinstance(temp, float):
          devices.append(SensorDevice(id, temp, lat, lon, timestamp, name, poller_entity))
          _LOGGER.info("Adding sensor: " + str(id))

        else:
          devices.append(SensorDevice(id, None, lat, lon, timestamp, name, poller_entity))
          _LOGGER.info("Adding faulty sensor: " + str(id) + " (temperature missing)")

    add_devices(devices)

class SensorDevice(Entity):
    def __init__(self, id, temperature, latitude, longitude, timestamp, name, poller_entity):
        self._device_id = id
        self._state = temperature
        self._entity_id = 'sensor.badtemp_' + str.lower(self._device_id)
        self._latitude = latitude
        self._longitude = longitude
        self._timestamp = timestamp
        self._friendly_name = name
        self._poller = poller_entity
        self.update()

    @Throttle(UPDATE_INTERVAL)
    def update(self):
        """Temperature"""

        if str.lower(self._device_id) == self._poller:
            ApiRequest.call()

        for jsonr in ReadJson().json_data()["Payload"]["swimAreas"]:
            if str.lower(jsonr["nameArea"]).replace("\xe5","a").replace("\xe4","a").replace("\xf6","o") == str.lower(self._device_id):
                if self._state is not None:
                  self._state = float(round(jsonr["temperatureWater"], 1))
                self._latitude = str(jsonr["geometryArea"]["y"])
                self._longitude = str(jsonr["geometryArea"]["x"])
                self._timestamp = datetime.datetime.strptime(str(jsonr["timeStamp"]).split('.')[0], "%Y-%m-%dT%H:%M:%S")
                _LOGGER.debug("Temp is " + str(self._state) + " for " + str(self._device_id))

    @property
    def entity_id(self):
        """Return the id of the sensor"""
        return self._entity_id
        _LOGGER.debug("Updating device " + self._entity_id)

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return '°C'

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._friendly_name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def state(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor"""
        return 'mdi:coolant-temperature'

    @property
    def device_class(self):
        """Return the device class of the sensor"""
        return 'temperature'

    @property
    def device_state_attributes(self):
        """Return the attribute(s) of the sensor"""
        if self._latitude is None or self._longitude is None:
            return {
                "lastUpdate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }
        else:
            return {
                "latitude": self._latitude,
                "longitude": self._longitude,
                "lastUpdate": self._timestamp
                }

class ApiRequest:

    def call():
        """Temperature"""
        _LOGGER.debug("Sending API request to: " + URL)
        response = urllib.request.urlopen(URL)
        response_json = json.dumps(json.loads(response.read()))
        _LOGGER.debug("Response: " + response_json)
        with open(PERS_JSON, "w") as outfile:
            json.dump(response_json, outfile)

        return True


class ReadJson:
    def __init__(self):
        self.update()

    @Throttle(UPDATE_INTERVAL)
    def update(self):
        """Temperature"""
        _LOGGER.debug("Reading " + PERS_JSON + " for device")
        with open(PERS_JSON) as json_file:
            json_datas = json.loads(json.load(json_file))
        self._json_response = json_datas

    def json_data(self):
        """Keep json data"""
        return self._json_response
