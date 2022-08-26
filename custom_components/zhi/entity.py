from homeassistant.const import CONF_NAME, CONF_ICON, CONF_UNIQUE_ID
from homeassistant.util import slugify
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

ZHI_SCHEMA = {
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_ICON): cv.string,
    vol.Optional(CONF_UNIQUE_ID): cv.string
}


class ZhiEntity:

    def __init__(self, conf, icon=None):
        self._attr_name = conf.get(CONF_NAME) or self.__class__.__name__
        self._attr_icon = conf.get(CONF_ICON) or icon
        self._attr_should_poll = False
        self._attr_unique_id = conf.get(CONF_UNIQUE_ID) or self.__class__.__name__.lower() + '.' + slugify(self._attr_name)


class ZhiPollEntity(ZhiEntity):

    data = None
    skip_poll = False

    @property
    def available(self):
        return self.data is not None

    @property
    def should_poll(self):
        if self.skip_poll:
            self.skip_poll = False
            return False
        return True

    async def async_update(self):
        try:
            self.data = await self.async_poll()
        except Exception as e:
            from logging import getLogger
            getLogger(__name__).error("Error on update: %s", e)
            self.data = None

    async def async_poll(self):
        return await self.hass.async_add_executor_job(self.poll)

    def poll(self):
        raise NotImplementedError
