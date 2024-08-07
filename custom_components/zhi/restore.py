from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.event import async_track_state_change_event

class ZhiRestoreEntity(RestoreEntity):

    state_sensor = None

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state:
            self.update_from_last_state(last_state)

        if self.state_sensor:
            async_track_state_change_event(self.hass, self.state_sensor, self.state_sensor_changed)
            state = self.hass.states.get(self.state_sensor)
            if state and state.state not in [STATE_UNKNOWN, STATE_UNAVAILABLE]:
                self.update_from_sensor(state)

    async def state_sensor_changed(self, entity_id, old_state=None, new_state=None):
        if new_state and new_state.state not in [STATE_UNKNOWN, STATE_UNAVAILABLE]: # and new_state != old_state
            if not self.update_from_sensor(new_state):
                self.async_write_ha_state()

    def update_from_last_state(self, state):
        pass

    def update_from_sensor(self, state):
        pass
