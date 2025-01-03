# Poet's Lens
A camera that prints poems of what it sees.

Forked from the [poetry camera ](https://poetry.camera/)by Ryan Mather and Kelin Carolyn Zhang. 

I worked with Richard Errico, a high-school teacher interested in photography and electronics. He thought this was a very cool project, so he wanted to make his own. 

We followed the same instructions that are in the original poetry camera github but we added the steps we did. Here is the 3D print we used: https://www.thingiverse.com/thing:6501240

## Software Steps

### Part 1. Check that your Raspberry Pi & camera works
1. Connect your Raspberry Pi to your Camera module. We used a different camera, such as the cable that came with the recommended camera, and the extra strips were too big on one side. You need the same size for both ends with the Pi. Here is the camera we used: https://www.raspberrypi.com/products/camera-module-3/ 

   To test your camera, use this command:
``` shell
raspistill -o testshot.jpg
```

3. Insert your SD card with a fresh install of any Raspberry Pi OS onto the Pi. We did Legacy for 32-bit. You can follow steps here to do that: https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/2. 

4. Connect your Pi to a monitor via mini HDMI.

5. Plug in power. You should see a green light on the Pi, and a start-up screen on the monitor.
  
7. Once the Pi is on, open up the Terminal on your Pi to start making changes.

8. Set up Raspberry Pi hardware to take Camera & Serial inputs:
   
```shell
sudo raspi-config
```

9. You'll want to adjust the following settings:
    - 6. Advanced Options -> Glamor -> On
    - 3. Interface Options -> Serial Port -> No -> Yes

    Restart the system as needed. You can either put in the command to restart or just unplug the power and then wait a few seconds before reconnecting power.
   
### Part 2. Check that your camera works
Use this tutorial to test the camera: (https://www.dummies.com/article/technology/computers/hardware/raspberry-pi/test-raspberry-pi-camera-module-246246/)

### Part 3. Check that your printer works
1. Update the system and install requirements. 
```shell
$ sudo apt-get update
$ sudo apt-get install git cups build-essential libcups2-dev libcupsimage2-dev python3-serial python-pil python3-unidecode
```

2. Install some software required to make the Adafruit Thermal Printer work. This works even with other thermal printers. 
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
$ git clone https://github.com/liapia99/Poet-Lens.git
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
You have to do this every time you power up your Pi. However, this should not be needed if the setup is done correctly. 

Our baud rate was different than the Adafruit and original GitHub, so just test 19200 and 9600 to see which one gives you an output on the printer. We had 9600. 

6. Open our `Poet-Lens` directory:
```shell
$ cd Poet-Lens
```

6. *If* your printer's baud rate is different from `19200`, open `main.py` and replace that number with your own printer's baud rate:
```shell
# main.py:

# instantiate printer
printer = Adafruit_Thermal('/dev/serial0', 9600, timeout=2)
```
7. *If* you want a different prompt for your camera you can copy and paste one of the options from 'prompts.md'. 

### Part 4. Set up the AI
1. Set up an OpenAI account and a Replicate account, as you will need to create two API keys. When we went through the original steps, we kept getting and Error Code : 404 : 'The model 'gpt-4' does not exist or you do not have access to it.' So this is how we solved our problem: 

2. Navigate to your directory with the Poetry Camera code and create a `.env` file, which will store sensitive details like your OpenAI API key. We named ours:
```.env```. If you give it a name like ```nano.env``` you must change this in the main.py. 

Create an OpenAI key. Since we were beginners with API keys, we had to figure out how to do this. Richard has a paid account with OpenAI, so we just had to go to the Billing page and click Add payment details. You need to pay for using an API key outside of the OPENAI playground. We just did $5. 

Our Pi was pretty slow when we opened the web browser, so we ended up doing everything on a separate computer. For the API keys, copy them and paste them into a Word or Notepad document. I also recommend changing the font to Courier New so that you can see the differences between the '0' or 'O' and 'I' or 'l'. 

Create a Replicate token at https://replicate.com/account/api-tokens. I just used the Default token given. We also had to pay to use the API model that creates the poem. For that, when you search for the blip-2 API model or go here: https://replicate.com/andreasjansson/blip-2, on the bottom left, in yellow, there should be a pop-up that prompts you to add billing details. It is not bad, though; for example, for this API, it costs $1 to run it 714 times. You can set a limit for each month. 


3. In the .env, add your API key and token:
```OPENAI_API_KEY=pasteyourAPIkeyhere```
```REPLICATE_API_TOKEN=pasteyourAPIkeyhere```

In the terminal, we had to store it as an environment variable instead of hard-coding it into the script. This is how we did it: 
```shell
$ export OPENAI_API_KEY=your_api_key_here
$ export REPLICATE_API_TOKEN=your_api_token_here
$ curl https://api.replicate.com/v1/account -H "Authorization: Bearer $REPLICATE_API_TOKEN"
```
The curl command should, if the previous steps are done correctly, connect to your Replicate API account and print out your GitHub name, handle, and your GitHub URL. 

The following commands should spit back out your API key and token.

```shell
$ echo "$REPLICATE_API_TOKEN"
$ echo "$OPENAI_API_KEY"
```

### Part 5. Get it working end-to-end

1. Connect buttons
```shell
$ pip install replicate
$ pip install python-dotenv
$ pip install openai
```
2. Run the poetry camera script. You should already be in the poetry-camera folder but if not:
   
```shell
$ cd Poet-Lens
```

```shell
$ python main.py
```

3. Check that the light on the Pi does not flash quickly. We did a separate LED and two buttons, but you can use the button that the original project suggested. 

4. Click the shutter button and wait for the poem to print out.


## Part 6. Automatically run the Poetry Camera code when the camera turns on

1. Set up a `cron` job to run your python script at startup. First, open your `crontab` file to your default editor:
```shell
$ crontab -e
```

2 Then add the following line to your `crontab`, to run the script when you boot up the computer.
```shell
# Run poetry camera script at start
@reboot /usr/bin/python3 /home/stemguy/Poet-Lens/main.py
```
On the left side of the terminal, our command line starts with ```stemguy@raspberrypi```. Anything in front of the ```@``` sign should replace ```stemguy``` in the command line above. Normally, it is just ```pi```. 

Press Ctrl and X and then Shift Y to make the changes. Enter. 

- Reboot the system for this to take effect
```shell
sudo reboot
```
Now reboot your camera. Once the green built-in LED on the Pi turns solid then you can press the shutter button.

A common problem that we had was that camera was failing. For that, we just rebooted the camera by unplugging and plugging back in the batteries. You can also try:

```shell
lsof /dev/video0
kill PID
```
This will stop the camera from running for anything else. It essentially "clears" it. 

## Part 7. Make the power circuit

![image](https://github.com/user-attachments/assets/7d01f2bd-1937-4c73-9c15-128eca2524a5)


<img width="1217" alt="image" src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/dca36686-fcfa-43ba-86f6-155bd1aab0e5">

## Part 8: Change wifi networks on-the-go
- Switched to Pi 3 B+ and Raspberry Pi HQ CCTV camera - you have to take off the CS mount
- https://www.raspberrypi.com/documentation/computers/camera_software.html
- https://forum.arducam.com/t/pi-hq-camera-lens-unable-to-focus/1006/2
- https://forums.raspberrypi.com/viewtopic.php?t=272917
