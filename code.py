# adafruit gemma m0 connected to LPD8806-48 LED strip with SPI port

import time
from rainbowio import colorwheel
import board
import busio
import sys
import array
import random

clock_pin = board.A1
data_pin = board.A2
num_pixels = 144 # counted 144
num_latch = 5 # int((num_pixels + 31) / 32)

print("start")
print("attempting to open SPI port")
print(f"clock_pin: {clock_pin} data_pin: {data_pin}")
try:
    spi = busio.SPI(clock_pin, data_pin)
    print("SPI port present")
except ValueError:
    print("no SPI port - exit")
    sys.exit(ValueError)

# get SPI lock
print("SPI lock attempt")
if not spi.try_lock():
    print("no SPI lock - exit")
    sys.exit(1)
print("SPI locked")

# configure the speed, phase, and polarity of the SPI bus for LPD8806
baudrate = 1000000 # datasheet says 20mhz max, but 1-2mhz typ
polarity = 1 # 1 = clock is idle when high
phase = 1 # 1 = sample on falling edge
print(f"configure SPI- baudrate:{baudrate}Hz, polarity:{polarity} phase:{phase}")
spi.configure(baudrate=baudrate,polarity=polarity,phase=phase)

# check actual frequency
baudrate_meas = spi.frequency
print(f"actual baudrate:{baudrate_meas}Hz")

# issue initial latch/reset
pixels = array.array("B", [0x80] * num_pixels * 3)
latch = array.array("B", [0] * 5)
print(f"pixels length: {len(pixels)} latch length: {len(latch)}")
print(f"initializing led strip; sending latch")
spi.write(latch)

# set pixels to off
print("setting pixels to off")
spi.write(pixels)
spi.write(latch)
time.sleep(1)

# set each pixel to a random colour
print("setting each pixel to a random colour")
for i in range(num_pixels):
    pixels[i*3+0] = 0x80 | random.getrandbits(7)
    pixels[i*3+1] = 0x80 | random.getrandbits(7)
    pixels[i*3+2] = 0x80 | random.getrandbits(7)
    spi.write(pixels)
    spi.write(latch)
    time.sleep(0.05)
time.sleep(1)

# move a white pixel along the line
print("white pixel chase")
for i in range(num_pixels):
    pix_start = i*3
    pix_stop = pix_start + 3
    saved = pixels[pix_start:pix_stop]
    pixels[pix_start:pix_stop] = array.array("B", [0xFF] * 3)
    spi.write(pixels)
    spi.write(latch)
    pixels[pix_start:pix_stop] = saved
    time.sleep(0.05)
spi.write(pixels)
spi.write(latch)
time.sleep(1)

# put the shopping cart back
print("release SPI lock and de-init")
spi.unlock()
spi.deinit()
