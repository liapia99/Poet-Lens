# Poetry Camera
A camera that prints poems of what it sees.

Forked from the [poetry camera ](https://poetry.camera/)by Ryan Mather and Kelin Carolyn Zhang. 

I worked with Richard Errico, a high-school teacher interested in photography and electronics. He thought this was a very cool project, so he wanted to make his own. 

We followed the same instructions that are in the original poetry camera github but we added the steps we did. 

## Software Steps

### Part 1. Check that your Raspberry Pi & camera works
1. Connect your Raspberry Pi to your Camera module. We used a different camera, such as the cable that came with the recommended camera, and the extra strips were too big on one side. You need the same size for both ends with the Pi. Here is the camera we used:

   To test your camera, use this command:
``` shell
raspistill -o testshot.jpg
```

3. Insert your SD card with a fresh install of any Raspberry Pi OS onto the Pi. You can follow steps here to do that: https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/2. 

4. Connect your Pi to a monitor via mini HDMI.

5. Plug in power. You should see a green light on the Pi, and a start-up screen on the monitor.
  
7. Once the Pi is on, open up the Terminal on your Pi to start making changes.

8. Set up Raspberry Pi hardware to take Camera & Serial inputs:
```shell
sudo raspi-config
```

9. You'll want to adjust the following settings:
    - Glamor: ON (for Camera setup on newer versions of Raspbian OS)
    - Serial Port ON (lets you access receipt printer inputs)
    - Serial Console OFF (idk what this does)

    Restart the system as needed.
   
Use this tutorial to test the camera: (https://www.dummies.com/article/technology/computers/hardware/raspberry-pi/test-raspberry-pi-camera-module-246246/)

### Part 2. Check that your printer works
1. Update the system and install requirements. I'm not sure you even need all of these; I can go over these again later and trim out the unnecessary ones.
```shell
$ sudo apt-get update
$ sudo apt-get install git cups build-essential libcups2-dev libcupsimage2-dev python3-serial python-pil python-unidecode
```

2. Install some software required to make the Adafruit Thermal Printer work.
```shell
$ cd
$ git clone https://github.com/adafruit/zj-58
$ cd zj-58
$ make
$ sudo ./install
```

3. Clone this repo, which contains our Poetry Camera software:
```shell
$ cd
$ git clone https://github.com/carolynz/poetry-camera-rpi.git
```

4. Set up your thermal printer, connecting it to power and your Pi. Both the the TTL and power should be connected to the Pi and batteries. ![image](https://github.com/user-attachments/assets/c6d9a1e5-1b92-40f5-8cd7-383cb450049a)
   Here is the printer we got: https://www.amazon.com/Maikrt-Embedded-Microcontroller-Secondary-Development/dp/B09YGVPPWV/ref=sr_1_3?

   In the Pi terminal, send these commands:

```shell
$ stty -F /dev/serial0 9600
$ echo -e "This is a test.\\n\\n\\n" > /dev/serial0
```
  We got a permission denied error. If that happens, just use this command:

  ```shell
$ sudo chmod 666 /dev/serial0
```

  Our baud rate was different than the Adafruit and original github so just test 19200 and 9600 to see which one gives you an output on the printer. 



  
6. Open our `poetry-camera-rpi` directory:
```shell
$ cd poetry-camera-rpi
```

6. *If* your printer's baud rate is different from `19200`, open `main.py` and replace that number with your own printer's baud rate:
```shell
# main.py:

# instantiate printer
printer = Adafruit_Thermal('/dev/serial0', 19200, timeout=5)
```

[TODO] need a setup script to test that the printer works

### Part 3. Set up the AI
1. Set up an OpenAI account and create an API key.

2. Navigate to your directory with the Poetry Camera code and create a `.env` file, which will store sensitive details like your OpenAI API key:
```nano .env```

3. In the .env, add your API key:
```OPENAI_API_KEY=pasteyourAPIkeyhere```

[TODO] add an openai test script


### Part 4. Get it working end-to-end
[TODO] include wiring diagram

1. Connect buttons
```shell
$ pip install replicate
$ pip install python-dotenv
$ pip install openai
sk-proj-oBtFtyJNZjbIESXY46q0T3BlbkFJ0B3apt56ttYWFzl3jKyU
```
2. Run the poetry camera script.
```shell
$ python main.py
```

3. Check that the shutter button lights up, indicating that the camera is ready to take a picture

4. Click the shutter button and wait for the poem to print out.

[TODO] troubleshooting instructions different common error messages

## Part 5. Automatically run the Poetry Camera code when the camera turns on

1. Set up a `cron` job to run your python script at startup. First, open your `crontab` file to your default editor:
```shell
$ crontab -e
```

2 Then add the following line to your `crontab`, to run the script when you boot up the computer.
```shell
# Run poetry camera script at start
@reboot python /home/pi/poetry-camera-rpi/main.py >> /home/pi/poetry-camera-rpi/errors.txt 2>&1
```
The `>> {...}errors.txt 2>&1` writes any error messages to `errors.txt` for debugging. A common failure mode is files cannot be found. Make sure that all your filepaths are absolute filepaths and have the right usernames and directory names.

- Reboot the system for this to take effect
```shell
sudo reboot
```
Now reboot your camera and wait for the LED light to turn on!


## Part 6. Make the power circuit
[TODO] clean this up & explain steps :)

<img width="1217" alt="image" src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/dca36686-fcfa-43ba-86f6-155bd1aab0e5">

## Part 7: Change wifi networks on-the-go
The camera needs wifi to work. You could always hardcode in your mobile hotspot by editing `wpa_supplicant.conf`. If you want to connect to new wifi networks on the fly, just follow [this simple tutorial](https://www.raspberrypi.com/tutorials/host-a-hotel-wifi-hotspot/) with plug-and-play code. (You can auto-run the tutorial's Flask app and our main camera code as two cron jobs at the same time.)

To do the above tutorial, you'll need a second wifi adapter, plugged into your microUSB port. Definitely get a plug-and-play wifi adapter that works for Linux/Raspberry Pi.

Wifi adapter options that seem to work:
- [From Pi Hut (UK)](https://thepihut.com/products/usb-wifi-adapter-for-the-raspberry-pi)
- [LOTEKOO, from Amazon](https://www.amazon.com/dp/B06Y2HKT75)
- [Canakit, from Amazon](https://www.amazon.com/dp/B00GFAN498)

MicroUSB to USB adapters:
- [From Amazon](https://www.amazon.com/Ksmile%C2%AE-Female-Adapter-SamSung-tablets/dp/B01C6032G0)
- [Super slim, from Adafruit](https://www.adafruit.com/product/2910)
