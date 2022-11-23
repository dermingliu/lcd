#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys 
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_1inch54
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO
import bme680
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# Raspberry Pi pin configuration:
tft =21
RST = 27
DC = 25
BL = 18
bus = 0 
device = 0 
logging.basicConfig(level=logging.DEBUG)
GPIO.setup(tft,GPIO.OUT)
GPIO.output(tft,1)
sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)
start_time = time.time()
curr_time = time.time()
burn_in_time = 30
burn_in_data = []
disp = LCD_1inch54.LCD_1inch54()
disp.Init()
# Clear display.
disp.clear()
Font1 = ImageFont.truetype("../Font/Font01.ttf",25)
Font2 = ImageFont.truetype("../Font/Font01.ttf",25)
Font3 = ImageFont.truetype("../Font/Font02.ttf",35)
image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
draw = ImageDraw.Draw(image1)
im_r=image1.rotate(270)
disp.ShowImage(im_r)
try:
    print('Collecting gas resistance burn-in data for 5 mins\n')
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)
    gas_baseline = sum(burn_in_data[-50:]) / 50.0
    gas_baseline = sum(burn_in_data[-50:]) / 50.0
    # Set the humidity baseline to 40%, an optimal indoor humidity.
    hum_baseline = 40.0
    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    hum_weighting = 0.25
    print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
        gas_baseline,
        hum_baseline))
    while True:
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            gas_offset = gas_baseline - gas

            hum = sensor.data.humidity
            hum_offset = hum - hum_baseline

            # Calculate hum_score as the distance from the hum_baseline.
            if hum_offset > 0:
                hum_score = (100 - hum_baseline - hum_offset)
                hum_score /= (100 - hum_baseline)
                hum_score *= (hum_weighting * 100)

            else:
                hum_score = (hum_baseline + hum_offset)
                hum_score /= hum_baseline
                hum_score *= (hum_weighting * 100)

            # Calculate gas_score as the distance from the gas_baseline.
            if gas_offset > 0:
                gas_score = (gas / gas_baseline)
                gas_score *= (100 - (hum_weighting * 100))

            else:
                gas_score = 100 - (hum_weighting * 100)

            # Calculate air_quality_score.
            air_quality_score = hum_score + gas_score
            air2 = int(air_quality_score)
            print('Gas: {0:.2f} Ohms,humidity: {1:.2f} %RH,air quality: {2:.2f}'.format(
                gas,
                hum,
                air_quality_score))
#            disp = LCD_1inch54.LCD_1inch54()
            # Initialize library.
#            disp.Init()
            # Clear display.
#            disp.clear()
            # Create blank image for drawing.
            image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
            draw = ImageDraw.Draw(image1)
            logging.info("draw text")
#            Font1 = ImageFont.truetype("../Font/Font01.ttf",25)
#            Font2 = ImageFont.truetype("../Font/Font01.ttf",35)
#            Font3 = ImageFont.truetype("../Font/Font02.ttf",32)
#            draw.rectangle([(0,65),(140,100)],fill = "WHITE")
            draw.text((5, 8), "Indoor air Quality", fill = "GREEN",font=Font1)
#            draw.rectangle([(0,115),(190,160)],fill = "RED")
            draw.text((5, 68),"Humi:", fill = "RED",font=Font2)
            draw.text((88, 68), str(hum), fill = "WHITE",font=Font3)
            draw.text((5, 110),"Air:", fill = "RED",font=Font2)
            draw.text((88, 110), str(air2), fill = "WHITE",font=Font3)
            im_r=image1.rotate(270)
            disp.ShowImage(im_r)
            time.sleep(5)
#            disp.module_exit()
#            logging.info("quit:")
#
except IOError as e:
    logging.info(e)    
except KeyboardInterrupt:
    disp.module_exit()
    logging.info("quit:")
    GPIO.output(tft,0)
    GPIO.cleanup()
    exit()
