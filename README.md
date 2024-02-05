# ImageGenBot

## Description

This is a Discord bot that can be used to generate images from text using Stable Diffusion.  It uses the [Auto1111SDK](https://github.com/Auto1111SDK/Auto1111SDK) python library and [Py-cord](https://pycord.dev).  There is a queue system built into the bot, but I haven't tested it using multiple servers.  Much like any other use of Stable Diffusion, you will need a beefy system to run this without errors or failure. 

This was mostly written for personal use, but I thought it would be a good idea to share it with others.  It is not perfect, but it works well enough for my needs.  Feel free to add on, change it, fork it, whatever.  I will be adding onto it with things I find fun or useful.  If you have any questions, feel free to ask.

The bot also features funny quotes from movies, tv shows, and games from my personal favorites.  These can be edited in `core/resources/messages.csv`.

### Preparation
#### Discord Bot
1. Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications)
2. Under OAuth2, select "bot" and "applications.commands"
3. Under Bot Permissions, select "Send Messages", "Attach Files", and "Use Slash Commands"
4. Copy the URL and add the bot to your server
5. Under Bot, select "Reset Token" and copy the newly created token

## Setup

### Docker (Recommended)

1. Clone the repository
2. Edit the ".env" file to include your bot token
3. Run `docker-compose up -d`

### Manual with virtual environment (Second best)

1. Clone the repository
2. Edit the ".env" file to include your bot token
3. Run `python -m venv venv`
4. Run `source venv/bin/activate`
5. Run `pip install -r requirements.txt`
6. Run `deactivate`
7. Run `venv/bin/python main.py`

### Manual without virtual environment

1. Clone the repository
2. Edit the ".env" file to include your bot token
3. Run `pip install -r requirements.txt`
4. Run `python main.py`

### Usage
#### First Run
1. If using SDXL, download the [sdxl-vae-fp16-fix.pt](https://huggingface.co/madebyollin/sdxl-vae-fp16-fix) file and put it in models/vae/ folder.  
2. Run the bot and use the `/download` command to download a model from CivitAI.
3. Fill in the URL of the model, the desired file name, and the model type.  **If it is an sdxl model, make sure the name you enter includes 'sdxl' in it.**
4. If the model requires an API key from CivitAI, it will return with an error.  Rerun the command and add your api key in the optional field.  You can find how to get an API key [here](https://education.civitai.com/civitais-guide-to-downloading-via-api/).
4. Run the `/update_settings` command to set the recommended settings for the model.  You will select the model from the dropdown, set the recommended CFG scale, Sampler name, and Clip Skip settings.

#### Normal Usage
#### Text2Image
1. Use the `/draw` command to generate an image.
2. Fill in the prompt section.  This is the text that will be used to generate the image.
3. Optionally, you can enter a Negative Prompt, select a Model Name (if none is selected, it will use the first one alphabetically), choose how many images you want to generate (max 4), choose the height and width of the photo from the dropdown (values are the suggested ones for SDXL models), and set the number of Steps the generator should take.

#### Image2Image
1. Use the `/redraw` command to generate an image using another image.
2. Attach the image you want to use as the starting point.
3. Fill in the prompt section.  This is the text that will be used to generate the image.
4. The height and width will be set by the size of the image you attached.  The program will find the closest aspect ratio that fits with the SDXL suggested sizes and resize the original image to match it.
5. Optionally, you can enter a Negative Prompt, select a Model Name (if none is selected, it will use the first one alphabetically), choose how many images you want to generate (max 4), and set the number of Steps the generator should take.

#### Upscale
1. Use the `/upscale` command to upscale an image.
2. Attach the image you want to upscale.
3. Select the Upscaler you want to use.
4. Choose whether you want to upscale it by either 2 or 4 times.

## Disclaimer
I am not responsible for any misuse of this bot.  It is meant to be used for fun and learning.  Please do not use it to generate harmful or inappropriate images.  I will not be held responsible for any misuse of this bot.  Please use it responsibly.

I am not a programmer.  A lot of this was just trial and error, with the use of ChatGPT and Copilot along the way.  If you have suggestions to improve it, please let me know!