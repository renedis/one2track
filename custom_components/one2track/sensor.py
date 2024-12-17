from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class One2TrackSensor(CoordinatorEntity, SensorEntity):
    """One2Track Sensor Entity."""

    def __init__(self, coordinator, device, attribute, name, unit):
        super().__init__(coordinator)
        self._device = device
        self._attribute = attribute
        self._attr_name = f"{name}"
        self._attr_unit_of_measurement = unit
        self._attr_unique_id = f"one2track_{device['uuid']}_{attribute}"

    @property
    def state(self):
        return self._device["last_location"].get(self._attribute)
