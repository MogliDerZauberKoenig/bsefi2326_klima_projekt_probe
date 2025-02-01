# bsefi2326_klima_projekt_probe
 
# Dokumentation: Raspberry Pi Lüftersteuerung mit Temperatursensor

## Einleitung
Dieser Python-Code steuert einen Lüfter basierend auf der gemessenen Temperatur eines DS18B20-Temperatursensors, der über den 1-Wire-Bus mit einem Raspberry Pi verbunden ist. Zudem sendet das System Temperaturdaten an eine API.

---

## Voraussetzungen
- **Hardware:**
  - Raspberry Pi (mit GPIO-Unterstützung)
  - DS18B20-Temperatursensor
  - Relais-Modul
  - PWM-fähiger Lüfter
- **Software-Pakete:**
  - `RPi.GPIO` (für GPIO-Steuerung)
  - `w1thermsensor` (für den DS18B20-Sensor)
  - `requests` (für die API-Kommunikation)
  - `threading` (für parallele Datenverarbeitung)


## Setup
```python
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
import time
import requests
import threading
```
- `RPi.GPIO`: Steuerung der GPIO-Pins
- `w1thermsensor`: Zugriff auf den Temperatursensor
- `requests`: API-Anfragen senden
- `threading`: Gleichzeitiges Senden der Temperaturwerte und Steuerung des Lüfters

---

## Globale Variablen
```python
GPIO.setmode(GPIO.BCM)
relaisPin = 18
pwmPin = 19
apiUrl = "http://localhost:5000/api/temp/insert"
targetTemp = 22.0
probeInterval = 1.0  # Abfrageintervall in Sekunden
```
- `relaisPin`: GPIO-Pin für das Relais
- `pwmPin`: GPIO-Pin für den PWM-gesteuerten Lüfter
- `apiUrl`: Endpunkt zur Speicherung der Temperaturdaten
- `targetTemp`: Zieltemperatur
- `probeInterval`: Messintervall

---

## GPIO-Initialisierung
```python
GPIO.setup(relaisPin, GPIO.OUT)
GPIO.setup(pwmPin, GPIO.OUT)
pwm = GPIO.PWM(pwmPin, 100)
pwm.start(0)
relaisIsOff = True
sensor = W1ThermSensor()
```
- Setzt die GPIO-Pins für das Relais und den Lüfter.
- Initialisiert das PWM-Signal für den Lüfter.
- Definiert `relaisIsOff`, um den Relais-Zustand zu verwalten.
- Initialisiert den Temperatursensor.

---

## Funktion zur Lüftersteuerung
```python
def fanSpeed(currentTemp: float, temp: float) -> int:
    if currentTemp <= temp:
        return 0
    
    diff = currentTemp - temp
    speed = min(10 + diff * 10 + (diff ** 1.8) * 3, 100)

    if speed < 10:
        speed = 10

    return int(speed)
```
- Berechnet die Lüftergeschwindigkeit basierend auf der aktuellen Temperatur.
- Wenn die Temperatur unter der Zieltemperatur liegt, bleibt der Lüfter aus.
- Andernfalls wird eine dynamische Geschwindigkeit berechnet.


```python
def controlFan(speed: int):
    global relaisIsOff
    
    if speed == 0:
        relaisIsOff = True
        GPIO.output(relaisPin, GPIO.LOW)
        pwm.ChangeDutyCycle(speed)
    else:
        if relaisIsOff:
            relaisIsOff = False
            GPIO.output(relaisPin, GPIO.HIGH)
        pwm.ChangeDutyCycle(speed)
```
- Schaltet das Relais ein oder aus.
- Ändert die Lüftergeschwindigkeit über PWM.

---

## Funktion zur API-Datenübertragung
```python
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
```
- Sendet Temperaturdaten an die API.
- Nutzt `try-except`, um Fehler beim Senden abzufangen.

---

## Hauptfunktion
```python
def main():
    while True:
        temp = sensor.get_temperature()
        speed = fanSpeed(temp, targetTemp)
        print(speed)
        if temp is not None:
            threading.Thread(target=sendData, args={temp}, daemon=True).start()
            threading.Thread(target=controlFan, args={speed}, daemon=True).start()
        
        time.sleep(probeInterval)
```
- Liest die Temperatur aus.
- Berechnet die Lüftergeschwindigkeit.
- Startet Threads für die API-Sendung und die Lüftersteuerung.
- Wartet `probeInterval` Sekunden, bevor die nächste Messung beginnt.

---

## Programmstart
```python
if __name__ == "__main__":
    main()
```
- Stellt sicher, dass das Skript nur gestartet wird, wenn es direkt ausgeführt wird (nicht als Modul importiert).

---
