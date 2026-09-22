from ssd1306 import SSD1306_I2C
from machine import Pin, I2C

sda_pin = Pin(6, Pin.OUT)
scl_pin = Pin(7, Pin.OUT)
weite = 128
höhe = 64

i2c = I2C(0, sda=sda_pin, scl=scl_pin, freq=400000)
oled = SSD1306_I2C(weite, höhe, i2c, addr=0x3C)

