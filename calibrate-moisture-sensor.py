from blib_moisture import MoistureSensor
import time

moisture_sensor = MoistureSensor(pin=26)

print("Expose the sensor to air.")
print("The sensor will read 5 values and calculate the average.")
print("The calibration process will begin in 10 seconds...")
time.sleep(10)

readings = []
for i in range(5):
    moisture = moisture_sensor.read_raw()
    readings.append(moisture)
    print(f"Reading {i + 1}: {moisture}")
    time.sleep(5)

air_moisture = sum(readings) / len(readings)
print(f"Average moisture level: {air_moisture}")

print("Submerge the sensor in water.")
print("The sensor will read 5 values and calculate the average.")
print("The calibration process will begin in 10 seconds...")
time.sleep(10)

readings = []
for i in range(5):
    moisture = moisture_sensor.read_raw()
    readings.append(moisture)
    print(f"Reading {i + 1}: {moisture}")
    time.sleep(5)

water_moisture = sum(readings) / len(readings)
print(f"Average moisture level: {water_moisture}")

print("Calibration complete. The sensor is now ready for use.")
print("You can now use the sensor in your main application.")
print("Make sure to adjust the thresholds based on the average values obtained during calibration.")

print(f"Air moisture level (minimum): {air_moisture}")
print(f"Water moisture level (maximum): {water_moisture}")
