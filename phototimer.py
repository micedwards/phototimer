import os
import time
import yaml
import logging
import logzero
from logzero import logger
from datetime import datetime
from config import config
from astral.geocoder import database, lookup
from astral.sun import sun
from pytz import timezone


def try_to_mkdir(path):
    if os.path.exists(path) is False:
        os.makedirs(path)
    return


def prepare_dir(base, now):
    path = '{:%Y%m%d}'.format(now)
    try_to_mkdir(base + "/" + path)
    path = '{:%Y%m%d/%Y%m%d_%H}'.format(now)
    try_to_mkdir(base + "/" + path)
    return path


def make_os_command(config, exposureMode, file_name):
    height = str(config["height"])
    width = str(config["width"])
    quality = str(config["quality"])
    metering_mode = str(config["metering_mode"])
    nightSSpeed = str(config["nightSSpeed"])
    ISO = str(config["ISO"])
    brightness = str(config["brightness"])
    contrast = str(config["contrast"])
    flip_horizontal = config["flip_horizontal"]
    flip_vertical = config["flip_vertical"]

    os_command = "/opt/vc/bin/raspistill -q " + quality + " "

    if flip_horizontal:
        os_command = os_command + "-hf "
    if flip_vertical:
        os_command = os_command + "-vf "

    os_command = os_command + "-h " + height + " -w " + width

    if exposureMode == 'night':
        os_command = os_command + \
            " -ISO " + ISO + " -ss " + nightSSpeed + \
            " -drc off -br " + brightness + " -co " + contrast + \
            " --metering " + metering_mode + " -o " + file_name
    else:
        os_command = os_command + " --exposure " + exposureMode + \
            " --metering " + metering_mode + " -o " + file_name
    return os_command


def check_shot(am, pm):
    now = str(datetime.now().time()).split(':')
    now = int(now[0] + now[1])
    if now > am and now < pm:
        return True
    return False


def run_loop(config):
    delta = 0
    base = config["base_path"]

    debugLog = config["debugLog"]

    # assumption that this program won't run for weeks so calc dawn/dusk once
    # check location is in astral db via online documentation
    city = lookup(config["location"], database())
    citysun = sun(city.observer, date=now)
    Dawn = citysun["dawn"].astimezone(timezone(city.timezone)).time()
    Dusk = citysun["dusk"].astimezone(timezone(city.timezone)).time()

    while True:
        # grab config file
        try:
            filepath = config["base_path"] + "/config.yaml"
            with open(filepath) as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                debugLog = config["debugLog"]
        except FileNotFoundError:
            logger.info("--<opening '%s' failed>---", filepath)

        if debugLog:
            logger.info(" ")
            logger.info("=========== start capture ==========")

        now = datetime.now()
        startTime = config["start_time"]
        endTime = config["end_time"]
        pause = config["time_delay"]

        if debugLog:
            logger.info("Pause interval: %s", str(pause))

        # set exposure or drop out of loop if night mode
        nowTime = now.time()
        if Dawn < nowTime and nowTime < Dusk:
            # Day
            if config["shooting_mode"] == "night":
                if debugLog:
                    logger.info("Shot cancelled as time is outside time window")
                continue
            exposureMode = 'auto'
        else:
            # Night
            exposureMode = 'night'

        take_shot = check_shot(startTime, endTime)

        if take_shot is True:
            path = prepare_dir(base, now)
            name = '{:%Y%m%d-%H%M%S-}'.format(now) + exposureMode + '.jpg'
            if debugLog:
                logger.info("Capturing %s in %s mode", name, exposureMode)

            fileName = base + "/" + path + "/" + name

            os_command = make_os_command(config, exposureMode, fileName)
            os.system(os_command)
            if debugLog:
                logger.info("Command: %s", os_command)

            delta = int((datetime.now() - now).seconds)
            if debugLog:
                logger.info("Capture File:  %s/%s secs", str(delta), str(pause))
        else:
            if debugLog:
                logger.info("Shot cancelled as time is outside time window")
        # night shots take about 10 x shooting time
        if pause - delta > 0:
            time.sleep(pause - delta)


if(__name__ == '__main__'):
    # logging added to track info for tweaking
    logzero.logfile(config["base_path"] + "/logfile.log", maxBytes=150000, backupCount=2)
    logzero.loglevel(logging.INFO)

    try:
        run_loop(config)
    except KeyboardInterrupt:
        logger.info("Capture cancelled by keyboard interrupt")
