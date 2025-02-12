class DailyCounter:
    def __init__(self, hass, name, initial_value=0):
        """Inicializa un contador diario."""
        self.hass = hass
        self.name = name
        self._value = initial_value

    @property
    def value(self):
        return self._value

    def increment(self):
        """Incrementa el contador."""
        self._value += 1

    def reset(self):
        """Resetea el contador a 0."""
        self._value = 0
