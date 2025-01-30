import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
import time
import requests
import threading

GPIO.setmode(GPIO.BCM)
relaisPin = 18
pwmPin = 19

apiUrl = "http://localhost:5000/api/temp/insert"
targetTemp = 22.0
probeInterval = 1.0 # <- in Sekunden

GPIO.setup(relaisPin, GPIO.OUT)
GPIO.setup(pwmPin, GPIO.OUT)

pwm = GPIO.PWM(pwmPin, 100)
pwm.start(0)
relaisIsOff = True
sensor = W1ThermSensor()

def fanSpeed(currentTemp: float, temp: float) -> int:
    if currentTemp <= temp:
        return 0
    
    diff = currentTemp - temp
    speed = min(10 + diff * 10 + (diff ** 1.8) * 3, 100)

    if speed < 10: speed = 10

    return int(speed)

"""while True:
    try:
        temperature = sensor.get_temperature()
    except SensorNotReadyException:
        print(f"Sensor Error: {e}")

    speed = fanSpeed(float(temperature), targetTemp)

    if speed == 0:
        relaisIsOff = True
        GPIO.output(relaisPin, GPIO.LOW)
        pwm.ChangeDutyCycle(speed)
    else:
        if relaisIsOff:
            relaisIsOff = False
            GPIO.output(relaisPin, GPIO.HIGH)
        pwm.ChangeDutyCycle(speed)"""

def sendData(temp: float):
	payload = { "value": temp }

	try:
		resp = requests.post(apiUrl, json=payload, timeout=5)
		if resp.status_code == 200:
			print(f"Gesendet: {payload}")
		else:
			print(f"Fehler {resp.status_code}: {resp.text}")
	except requests.exceptions.RequestException as e:
		print(f"Fehler: {e}")

def main():
	while True:
		temp = sensor.get_temperature()
		if temp is not None:
			threading.Thread(target=sendData, args={temp}, daemon=True).start()
        
		time.sleep(probeInterval)

if __name__ == "__main__":
    main()