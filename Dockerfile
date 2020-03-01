FROM balenalib/raspberry-pi-python:latest-run
ENTRYPOINT []
RUN apt-get update && apt-get install libraspberrypi-bin=1.20180328-1~nokernel1 libraspberrypi0=1.20180328-1~nokernel1 python3-pip --allow-downgrades -y
RUN pip3 install astral pyyaml logzero 
COPY . .
VOLUME /home/pi/image/
COPY ./config.yaml /home/pi/image/
CMD ["python3", "phototimer.py"]
