import time
from machine import Pin


# num = 4
# frequenz = 4000
# dc = (2**16 - 1)/100

# ----KOnfiguration----
class MorseCode:

    def __init__(self):
        self.led = Pin(3, Pin.OUT, pull=Pin.PULL_DOWN, value=0)

        self.dot = 200 * 2  # [ms] eine Einheit

        self.dash = 600 * 2  # [ms] ca. 3 Einheiten

        self.space_letter = 200 * 2  # [ms] pause innerhalb des gemorsten codes
        self.space_letters = 900 * 2  # [ms] pause zwischen Buchstaben eines Wortes

        self.space_words = 1400 * 2  # [ms] pause zwischen einzelnen gemorsten Wörtern

    def play_morse_code(self):
        for k in range(0, 5):
            # ---- D ----
            self.led.value(1)
            print("dash")
            time.sleep_ms(self.dash)
            for _ in range(0, 2):
                self.led.value(0)
                time.sleep_ms(self.space_letter)
                self.led.value(1)
                print("dot")
                time.sleep_ms(self.dot)

            self.led.value(0)
            time.sleep_ms(self.space_letters)

            print("D")

            # ---- A ----
            self.led.value(1)
            print("dot")
            time.sleep_ms(self.dot)

            self.led.value(0)
            time.sleep_ms(self.space_letter)

            self.led.value(1)
            print("dash")
            time.sleep_ms(self.dash)

            self.led.value(0)
            time.sleep_ms(self.space_letters)
            print('A')

            # ---- F ----
            for _ in range(0, 2):
                self.led.value(1)
                print(self.dot)
                time.sleep_ms(self.dot)
                self.led.value(0)
                time.sleep_ms(self.space_letter)

            self.led.value(1)
            print("dash")
            time.sleep_ms(self.dash)
            self.led.value(0)
            time.sleep_ms(self.space_letter)
            self.led.value(1)
            print("dot")
            time.sleep_ms(self.dot)

            print('F')

            self.led.value(0)
            time.sleep_ms(self.space_words)
            print(f"Durchgang: {k}")