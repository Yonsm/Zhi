from homeassistant.const import CONF_NAME, CONF_ICON, CONF_UNIQUE_ID
from homeassistant.util import slugify
import homeassistant.helpers.config_validation as cv
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

ZHI_SCHEMA = {
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_ICON): cv.string,
    vol.Optional(CONF_UNIQUE_ID): cv.string
}


class ZhiEntity:

    def __init__(self, conf, icon=None):
        self._name = conf.get(CONF_NAME) or self.__class__.__name__
        self._icon = conf.get(CONF_ICON) or icon
        self._unique_id = conf.get(CONF_UNIQUE_ID) or self.__class__.__name__.lower() + '.' + slugify(self._name)

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False


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
            _LOGGER.error("Error on update: %s", e)
            self.data = None

    async def async_poll(self):
        return await self.hass.async_add_executor_job(self.poll)

    def poll(self):
        raise NotImplementedError
