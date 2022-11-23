#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import RPi.GPIO as GPIO
import os
import sys
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_1inch54
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# Raspberry Pi pin configuration:
tft = 21
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)
GPIO.setup(tft,GPIO.OUT)
GPIO.output(tft,1)
try:
    # display with hardware SPI:
    ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
    #disp = LCD_1inch54.LCD_1inch54(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
    disp = LCD_1inch54.LCD_1inch54()
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()
    logging.info("show image")
    image1 = Image.open('../pic/all.bmp')
    im_r1=image1.rotate(90)
    disp.ShowImage(im_r1)
    time.sleep(5)
    image2= Image.open('../pic/iris.bmp')
    im_r2=image2.rotate(90)
    disp.ShowImage(im_r2)
    time.sleep(5)
    image3=Image.open('../pic/olive.bmp')
    im_r3=image3.rotate(90)
    disp.ShowImage(im_r3)
    time.sleep(5)
    disp.module_exit()
    logging.info("quit:")
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    disp.module_exit()
    GPIO.output(tft,0)
    GPIO.cleanup()
    logging.info("quit:")
    exit()
