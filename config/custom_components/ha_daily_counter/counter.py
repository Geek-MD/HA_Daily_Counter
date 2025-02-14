class DailyCounter:
    def __init__(self, hass, name, initial_value=0):
        self.hass = hass
        self.name = name
        self._value = initial_value

    @property
    def value(self):
        return self._value

    def increment(self):
        self._value += 1

    def reset(self):
        self._value = 0
