# Timelapse for Raspberry Pi based on Alex Ellis's blog post

Base: [https://blog.alexellis.io/raspberry-pi-timelapse/](https://blog.alexellis.io/raspberry-pi-timelapse/)

**An incomplete rundown.**

Read above blog for the background on why docker but check around to install 
docker as that process has changed since then. I use Ansible to configure
up my RPi with the basic setup and docker so I rarely setup manaually.

Raspberry Pi & Pi camera needed. I've been using two setups:

Raspberry Pi Zero W + camera in an offical case which is attached to an 
USB battery. I use this on an angled stand in an altered cardboard box
to control side light falling on the lens. Normally I have this sitting 
outside on the windowsill which external power pointing to the southern 
sky but have used it battery powered outside when stargazing.  The base 
OS setup has docker installed and it can either connect to the house wifi 
or my iPad to get NTP updates and to let me ssh into it. 

Second setup is a Zero W using a ZeroView 'case' [The PiHut] and a realtime 
clock. This setup I use mounted on windows in hotels (especially high up). 
The Pi is setup to connect to my iPad in hotspot mode so I can add the 
hotel wifi but with realtime clock it doesn't need that. Cool for city 
view timelapses but use a big SD card.


The program loops and uses parameters set via a config file to decide 
when and how the pictures are taken. Copy config.yaml to base directory 
and modify to your requirements.

If you use the docker container there is no need to rebuild when you want 
to tweak it as config.yaml is read before every shot. So you can set your 
location, the shooting day's start and end time or even tweak raspistill 
arguments while the program is running. 

I haven't installed it directly on a Pi for a long time so this might not 
be complete but these Python3 libraries are needed: 
- astral 
- pyyaml 
- logzero

Check the program and dockerfile for more details.

Configurationwise check astral documentation for location cities. 
I try to match time zone city [https://astral.readthedocs.io/en/latest/](https://astral.readthedocs.io/en/latest/)

If you have the Pi, camera, docker and config ready then:

```
docker run --name capture --volume /home/pi/image:/home/pi/image\
           --privileged --restart=always --env TZ="Australia/Sydney"\
           --detach micedwards/phototimer:latest`
```

Replace the TZ environment variable with your location's timezone.


Dockerfile stuff you probably can skip:
The dockerfile here is different to Alex's as it has been updated to use 
balenalib buster as the base image rather than resin. This lead to 
raspistill failing so I've had to roll back the libraries containing 
the raspistill programs to:
```
        libraspberrypi-bin=1.20180328-1~nokernel1 
        libraspberrypi0=1.20180328-1~nokernel1
``` 
 [as of 2020.03.01] 

Debug logging is switchable via the config file. Creates logfile in base 
path directory. 


**Files:**
```
phototimer
    +-- config.py     ! initial configuration
    +-- config.yaml   ! localised configuration (edit on the fly)
    +-- Dockerfile    
    +-- phototimer.py
    +-- README.md
```

Default config.yaml:
```
---
location: "Sydney"          ! used to calculate dawn/dusk for exposure mode
start_time: 1
end_time: 2359
flip_horizontal: False      ! check raspistill documentation
flip_vertical: False        ! check raspistill documentation
metering_mode: "matrix"     ! check raspistill documentation
shooting_mode: "normal"     ! "night" for no shots during dawn to dusk
base_path: "/home/pi/image"
width: 3280                 ! check raspistill documentation
height: 2464                ! check raspistill documentation
quality: 85                 ! check raspistill documentation
time_delay: 60              ! check raspistill documentation
ISO: 200                    ! check raspistill documentation
brightness = 48             ! check raspistill documentation
contrast = 3                ! check raspistill documentation
nightSSpeed: 5700000        ! check raspistill documentation
debugLog: False
```


Default configuration on boot provided by config.py:
```
config = {}
config["start_time"] = 1          
config["end_time"] = 2359         
config["location"] = "Sydney"

config["flip_horizontal"] = False
config["flip_vertical"] = False
config["metering_mode"] = "matrix"
config["shooting_mode"] = "normal"

config["height"] = 2464
config["width"] = 3280
config["quality"] = 85

config["base_path"] = "/home/pi/image"
config["time_delay"] = 60

config["ISO"] = 200
config["brightness"] = 48
config["contrast"] = 3
config["nightSSpeed"] = 5700000

config["debugLog"] = True
```


Here in case I forget the basics again...

**Build Pi:**

`docker build -t micedwards/phototimer:{date} .`
`docker push micedwards/phototimer:{date}`

Once working:
```
docker image tag micedwards/phototimer:{date} micedwards/phototimer:latest
docker push micedwards/phototimer:latest
```

**Camera Pi:**
```
docker run --name capture --volume /home/pi/image:/home/pi/image\
           --privileged --restart=always --env TZ="Australia/Sydney"\
           --detach micedwards/phototimer:latest 
```
(or use the date tag if troubleshooting)

**Troubleshooting:**

Local logs in base directory also check:
`docker container logs capture`

To connect to running container for debugging:
`docker exec -it capture bash`


**Cleaning up:**

`docker container stop capture`

Clear all pictures & logfiles from bash directory:
`sudo rm -r ~/image/20* && sudo rm -r ~/image/log*`

Delete all docker logs:
`sudo find /var/lib/docker/containers/ -type f -name "*.log" -delete`

`docker container start capture`

