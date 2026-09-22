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
WAKE_PIN = Pin(3, Pin.IN, Pin.PULL_DOWN, value=0)
LIGHT_SLEEP = 30000  # ms
HIGH_TRIGGER = esp32.WAKEUP_ANY_HIGH
LOW_TRIGGER = esp32.WAKEUP_ALL_LOW

# Sende Zeit von 2200 ms um garantiert ein Packet im Rythmus des Empfängers zu verschicken.
# Beachte: Sende Zeit diktiert implizit den delay der Interaktion.
# Empfänger: Rythmus von 200 ms mit wach: 150 ms, 1800 ms
SENDE_ZEIT = 2.2 * 1e3

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

    sender.deinit_sender()

    print("Trigger-Pin Initialisiert")

    # Konfiguration vor dem Schlafgehen,
    # damit der Pin auf GND bleibt und nicht hochgezogen wird.
    # [BEACHTE]: Button möchte any low haben / Potentiometer braucht any high
    esp32.wake_on_gpio([WAKE_PIN], LOW_TRIGGER)
    WAKE_PIN.init(hold=True)
    esp32.gpio_deep_sleep_hold(True)

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
