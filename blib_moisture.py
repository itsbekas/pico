from machine import ADC, Pin

class MoistureSensor:
    def __init__(self, pin: int | ADC, air_moisture: int = 0, water_moisture: int = 65535):
        """
        It's typically expected that air_moisture is the minimum value
        and water_moisture is the maximum value.

        Some sensors may be inverted, meaning that the values are reversed.
        Despite that, we will always treat air_moisture as the minimum
        and water_moisture as the maximum.
        """
        self.pin = pin if isinstance(pin, ADC) else ADC(Pin(pin))
        self.min = min(air_moisture, water_moisture)
        self.max = max(air_moisture, water_moisture)

    def read_raw(self) -> float:
        return self.pin.read_u16()

    def read_percentage(self) -> float:
        raw_value = self.read_raw()
        return raw_value / 65535 * 100

    def read_moisture(self) -> float:
        """
        Returns the moisture level as a percentage
        relative to the calibration values.
        0% is the minimum (air moisture)
        100% is the maximum (water moisture).
        """
        adjusted_raw_value = self.read_raw() - self.min
        adjusted_max = self.max - self.min
        return adjusted_raw_value / adjusted_max * 100
