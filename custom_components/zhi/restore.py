from homeassistant.helpers.restore_state import RestoreEntity


class ZhiRestoreEntity(RestoreEntity):

    state_sensor = None

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state:
            self.update_from_last_state(last_state)

        if self.state_sensor:
            self.hass.helpers.event.async_track_state_change(self.state_sensor, self.state_sensor_changed)
            state = self.hass.states.get(self.state_sensor)
            if state:
                self.update_from_sensor(state)

    async def state_sensor_changed(self, entity_id, old_state, new_state):
        if new_state:
            self.update_from_sensor(new_state)
            await self.async_update_ha_state()

    def update_from_last_state(self, state):
        pass

    def update_from_sensor(self, state):
        pass
