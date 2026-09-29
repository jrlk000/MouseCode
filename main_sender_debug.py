import machine
import time
import esp32
from machine import Pin, ADC
from sender import Sender

# Kommunikation
MSG_KISTE = "Motor"
MAC_KISTE = b'\x08\xb6\x1fo.\xe4'  # (Wroover)
MSG_LEUCHTE = "Leuchte"
MAC_LEUCHTE = b'\xb0\xa6\x04\x07R8'  # (Morse-Code Xiao) (string)b0:a6:04:07:52:38 ; (bytes)b'\xb0\xa6\x04\x07R8'

# Aufstehen / Schlafen gehen KOnfiguration
WAKE_PIN = Pin(2, Pin.IN, Pin.PULL_DOWN, value=0)
LIGHT_SLEEP = 30000  # ms
HIGH_TRIGGER = esp32.WAKEUP_ANY_HIGH
LOW_TRIGGER = esp32.WAKEUP_ALL_LOW

#Board Komponenten
OLED_I2C_ADDR = 0x3C
SDA_PIN = 5
SCL_PIN = 6
BUZZER_PIN = 4
SD_CS_PIN = 3

# Sende Zeit von 2200 ms um garantiert ein Packet im Rythmus des Empfängers zu verschicken.
# Beachte: Sende Zeit diktiert implizit den delay der Interaktion.
# Empfänger: Rythmus von 200 ms mit wach: 150 ms, 1800 ms
SENDE_ZEIT = 2.2 * 1e3
"""
Akku schonender Sende Rythmus: 
Ideen: Aufwachen nach dem Sleep benötigt mehrere 100 bis 250 ms soidasss das in die schlaf rythmus beachtet werden müsste. 
Wechsel in den Lihgt Sleep Modus für den Empfänger kürzt diese Zeit des aufwachens auf unter 2ms (Höher Stromverbrauch erstmal egal)
Kalibrierung des Rythmusese mit: 
Empfänger Schlafzeit 30ms
Empfänger Lausch-Zeit 5ms
Sender Sendezeit 45ms


Wechsel von Senden von Daten hin zu Senden von Zuständen um Zeiten weiter zu verkürzen. 

Möglich Implementierung:  
def send_state_burst(burst_duration_ms, state):
    # state ist eine Zahl von 0 bis 255. struct.pack packt sie in ein Byte.
    payload = bytes([state]) 
    start = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start) < burst_duration_ms:
        e.send(peer, payload)

# Sende den Status "1" (z.B. Knopf gedrückt) für 120ms
send_state_burst(120, 1)

"""


def power_down_oled():
    """Legt das OLED-Display per I2C-Kommando schlafen."""
    try:
        # I2C initialisieren
        i2c = machine.I2C(0, sda=machine.Pin(SDA_PIN), scl=machine.Pin(SCL_PIN))
        # 0x00 signalisiert Kommando, 0xAE ist der Display-OFF Befehl
        i2c.writeto(OLED_I2C_ADDR, b'\x00\xAE')
    except Exception as e:
        print("OLED nicht gefunden oder I2C Fehler:", e)

def prepare_base_board_for_sleep():
    """Bereitet die Hardware auf dem Base Board für minimalen Stromverbrauch vor."""
    # 1. OLED-Display in den Standby versetzen
    power_down_oled()

    # 2. I2C-Pins hochohmig schalten (Floating ohne Pull-Up/Down)
    # Verhindert Leckstrom durch die fest verbauten Pull-Up-Widerstände des Base Boards
    machine.Pin(SDA_PIN, machine.Pin.IN, None)
    machine.Pin(SCL_PIN, machine.Pin.IN, None)

    # 3. Buzzer Pin sicher auf LOW ziehen
    buzzer = machine.Pin(BUZZER_PIN, machine.Pin.OUT)
    buzzer.value(0)
    buzzer.init(hold=True)

    # 4. SD-Karte deaktivieren (Chip Select auf HIGH = inaktiv)
    sd_cs = machine.Pin(SD_CS_PIN, machine.Pin.OUT)
    sd_cs.value(1)
    sd_cs.init(hold=True)

try:
    # ---- Sender Initialisierung ----
    print("Initialisiere Sender...")
    sender = Sender()

    # ----Senden ----
    start = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start) < SENDE_ZEIT:
        sender.kontaktiere_empfänger(MAC_KISTE, MSG_KISTE)
        sender.kontaktiere_empfänger(MAC_LEUCHTE, MSG_LEUCHTE)
        print(f"Verbleibende Zeit {(SENDE_ZEIT - time.ticks_diff(time.ticks_ms(), start)) / 1000:.2f}")
        time.sleep_ms(50)

    #explizites Ausschalten der Peripherie Komponenten des Boardes
    prepare_base_board_for_sleep()

    #Deinitialisieren des Wlans.
    sender.deinit_sender()

    print("Trigger-Pin Initialisiert")

    # Konfiguration vor dem Schlafgehen,
    # damit der Pin auf GND bleibt und nicht hochgezogen wird.
    # [BEACHTE]: Button möchte any low haben / Potentiometer braucht any high
    esp32.wake_on_gpio([WAKE_PIN], LOW_TRIGGER)
    WAKE_PIN.init(hold=True)
    esp32.gpio_deep_sleep_hold(True)

    """
    Explicites Ausschalten der einzelnen aktiven Komponenten des Base Boards
    Oled Display per I2C zum ausschalten zwingen. 
    SDA und SCL Pins auf hochohmig setzen. 
    Buzzer Pin sichern 
    """

    time.sleep_ms(500)
    machine.deepsleep()

except KeyboardInterrupt:
    # Sauberes Aufräumen beim Beenden
    print("Programm beendet. Räume auf...")
    # blink_timer.deinit()
    # trigger.deinit()
    # led.value(0)
except Exception as e:
    # Fange unerwartete Hardware-Fehler ab
    print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")