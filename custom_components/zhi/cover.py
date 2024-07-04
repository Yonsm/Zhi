from enum import IntEnum
from .restore import ZhiRestoreEntity
from homeassistant.components.cover import CoverEntity, ATTR_POSITION, STATE_CLOSED, STATE_CLOSING, STATE_OPEN, STATE_OPENING
from homeassistant.helpers.event import async_track_utc_time_change, async_call_later

class ConverOperation(IntEnum):
    Open = 0
    Close = 1
    Stop = 2


class ZhiTravelCover(CoverEntity, ZhiRestoreEntity):

    _state = STATE_OPEN
    _position = 50
    _travel_time = 0
    _untrack = None

    def __init__(self, travel_time=0, position_sensor=None):
        self._travel_time = travel_time
        self.state_sensor = position_sensor

    @property
    def state(self):
        return self._state

    @property
    def current_cover_position(self):
        return self._position

    async def async_track_cover(self, op):
        async def async_tracking_cover(_):
            step = round(100 / self._travel_time)
            self._position += step * (1, -1)[op]
            if (self._position >= 100 if op == ConverOperation.Open else self._position < 0):
                self.untrack_cover()
                self.track_cover_end(op)
            self.async_write_ha_state()
        if self._travel_time:
            self._state = (STATE_OPENING, STATE_CLOSING)[op]
            self.untrack_cover()
            self._untrack = async_track_utc_time_change(self.hass, async_tracking_cover)
        else:
            self.track_cover_end(op)
            self.async_write_ha_state()

    def track_cover_end(self, op):
        self._state = (STATE_OPEN, STATE_CLOSED)[op]
        self._position = (100, 0)[op]

    def untrack_cover(self):
        if self._untrack is not None:
            self._untrack()
            self._untrack = None

    async def async_open_cover(self, **kwargs):
        if await self.control_cover(ConverOperation.Open):
            await self.async_track_cover(ConverOperation.Open)

    async def async_close_cover(self, **kwargs):
        if await self.control_cover(ConverOperation.Close):
            await self.async_track_cover(ConverOperation.Close)

    async def async_stop_cover(self, **kwargs):
        if await self.control_cover(ConverOperation.Stop):
            self._state = STATE_OPEN
            if self._travel_time:
                self.untrack_cover()
            else:
                self._position = 50
            self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs):
        position = kwargs.get(ATTR_POSITION)
        step = self._position - position
        if step == 0:
            return
        elif step > 0:
            await self.async_close_cover()
        else:
            step = -step
            await self.async_open_cover()
        if position > 0 and position < 100:
            async def async_pause_cover(_):
                await self.async_stop_cover()
            async_call_later(self.hass, self._travel_time * step / 100, async_pause_cover)

    def update_from_last_state(self, state):
        self._position = state.attributes.get('current_position', self._position)

    def update_from_sensor(self, state):
        if state.state in ('false', 'closed', 'off'):
            self._position = 0
            self._state = STATE_CLOSED
        else:
            self._state = STATE_OPEN
            if self._position == 0:
                self._position = 100
