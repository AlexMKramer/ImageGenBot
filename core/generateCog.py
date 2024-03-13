import discord
from discord import option
from discord.ext import commands
import os
import csv

import core.auto1111
import core.queueHandler
import core.utils as utils

wait_message = []


# Setup loras autocomplete
async def loras_autocomplete(ctx: discord.AutocompleteContext):
    loras = utils.get_loras()
    return [lora for lora in loras if lora.startswith(ctx.value.lower())]


# Setup checkpoint autocomplete
async def checkpoints_autocomplete(ctx: discord.AutocompleteContext):
    checkpoints = utils.get_checkpoints()
    return [checkpoint for checkpoint in checkpoints if checkpoint.startswith(ctx.value.lower())]


async def height_width_autocomplete(ctx: discord.AutocompleteContext):
    return [f"{hw['height']} {hw['width']}" for hw in utils.height_width_option]


async def sampler_autocomplete(ctx: discord.AutocompleteContext):
    return [sampler for sampler in utils.sampler_options if sampler.startswith(ctx.value.lower())]


async def controlnets_autocomplete(ctx: discord.AutocompleteContext):
    controlnets = utils.get_controlnets()
    return [controlnet for controlnet in controlnets if controlnet.startswith(ctx.value.lower())]


# set up the main commands used by the bot
class GenerateCog(commands.Cog, name="Generate", description="Generate images from text"):
    ctx_parse = discord.ApplicationContext
    core.queueHandler.queue_loop.start()

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description='Create images from text!', guild_only=True)
    @option(
        'prompt',
        str,
        description='A prompt to condition the model with.',
        required=True
    )
    @option(
        'negative_prompt',
        str,
        description='A negative prompt to condition the model with.',
        required=False
    )
    @option(
        'model_name',
        str,
        description='Choose the checkpoint to use for generating the images with.',
        required=False,
        autocomplete=checkpoints_autocomplete
    )
    @option(
        'num_images',
        int,
        min_value=1,
        max_value=4,
        description='The number of images to generate up to 4.',
        required=False
    )
    @option(
        'height_width',
        str,
        description='The height of the images to generate.',
        required=False,
        autocomplete=height_width_autocomplete
    )
    @option(
        'steps',
        int,
        description='The number of steps to take in the diffusion process.',
        required=False
    )
    async def draw(self, ctx: discord.ApplicationContext,
                   *,
                   prompt,
                   negative_prompt: str = "",
                   model_name,
                   num_images=4,
                   height_width="1024 1024",
                   steps=25
                   ):
        if model_name is None:
            # Get a list of the checkpoints
            model_name = utils.get_checkpoints()
            # Check if there are any checkpoints available
            if not model_name:
                # send a message to the user that there are no checkpoints and break the command
                await ctx.respond("There are no checkpoints available to use for generating images. Try downloading a "
                                  "model and placing it in the checkpoints folder.")
                return
            else:
                model_name = model_name[0]
        model_path = os.path.join(os.getcwd(), "models/checkpoints/" + model_name + ".safetensors")
        print(model_path)

        # Get the height and width from the user input
        height, width = height_width.split()
        height = int(height)
        width = int(width)

        # Get the default settings for the model chosen
        cfg_scale, sampler_name, clip_skip = utils.get_model_settings(model_name)

        # get a funny message
        funny_text = utils.funny_message()

        acknowledgement = await ctx.respond(f"**{funny_text}**\nGenerating {num_images} images for you!")
        # Send the request to the queue
        await core.queueHandler.add_request(funny_text, acknowledgement, "txt2img", prompt, negative_prompt,
                                            model_path, num_images, height, width, steps, cfg_scale, sampler_name,
                                            clip_skip)
        print(f"Added request to queue: {prompt}, {negative_prompt}, {num_images}, {height}, {width}, {steps},"
              f" {cfg_scale}, {sampler_name}")

    @commands.slash_command(description='Create images from an image!', guild_only=True)
    @option(
        'prompt',
        str,
        description='A prompt to condition the model with.',
        required=True
    )
    @option(
        'attached_image',
        description='The image to condition the model with.',
        required=True
    )
    @option(
        'percentage_of_original',
        int,
        min_value=1,
        max_value=100,
        description='The percentage of the original image to generate.',
        required=False
    )
    @option(
        'negative_prompt',
        str,
        description='A negative prompt to condition the model with.',
        required=False
    )
    @option(
        'model_name',
        str,
        description='Choose the checkpoint to use for generating the images with.',
        required=False,
        autocomplete=checkpoints_autocomplete
    )
    @option(
        'num_images',
        int,
        min_value=1,
        max_value=4,
        description='The number of images to generate up to 4.',
        required=False
    )
    @option(
        'steps',
        int,
        description='The number of steps to take in the diffusion process.',
        required=False
    )
    @option(
        'controlnet',
        str,
        description='Choose the controlnet to use for generating the images with.',
        required=False,
        autocomplete=controlnets_autocomplete
    )
    async def redraw(self, ctx: discord.ApplicationContext,
                     *,
                     prompt,
                     attached_image: discord.Attachment,
                     percentage_of_original: int = 50,
                     negative_prompt: str = "",
                     model_name,
                     num_images=4,
                     steps=25,
                     controlnet: str = ""
                     ):
        if model_name is None:
            # Get a list of the checkpoints
            model_name = utils.get_checkpoints()
            # Check if there are any checkpoints available
            if not model_name:
                # send a message to the user that there are no checkpoints and break the command
                await ctx.respond("There are no checkpoints available to use for generating images. Try downloading a "
                                  "model and placing it in the checkpoints folder.")
                return
            else:
                model_name = model_name[0]
        model_path = os.path.join(os.getcwd(), "models/checkpoints/" + model_name + ".safetensors")
        print(model_path)

        if "sdxl" in model_name & controlnet != "":
            await ctx.respond("You cannot use a controlnet with an SDXL model.")
            return

        # Get the default settings for the model chosen
        cfg_scale, sampler_name, clip_skip = utils.get_model_settings(model_name)

        # get a funny message
        funny_text = utils.funny_message()

        acknowledgement = await ctx.respond(f"**{funny_text}**\nGenerating {num_images} images for you!")
        # Send the request to the queue
        await core.queueHandler.add_request(funny_text, acknowledgement, "img2img", prompt, negative_prompt,
                                            model_path, num_images, steps, cfg_scale, sampler_name,
                                            clip_skip, attached_image, percentage_of_original, controlnet)
        print(f"Added request to queue: {prompt}, {negative_prompt}, {num_images}, {steps},"
              f" {cfg_scale}, {sampler_name}, {percentage_of_original}")

    @commands.slash_command(description='Upscale an image!', guild_only=True)
    @option(
        'attached_image',
        description='The image to upscale.',
        required=True
    )
    @option(
        'upscaler_name',
        str,
        choices=['R-ESRGAN AnimeVideo', 'R-ESRGAN 2x+', 'R-ESRGAN 4x+', 'R-ESRGAN 4x+ Anime6B',
                 'R-ESRGAN General 4xV3', 'R-ESRGAN General WDN 4xV3'],
        description='The upscaler to use.',
        required=True
    )
    @option(
        'scale',
        int,
        choices=[2, 4],
        description='The amount to upscale the image by.',
        required=True
    )
    async def upscale(self, ctx: discord.ApplicationContext,
                      attached_image: discord.Attachment,
                      upscaler_name,
                      scale
                      ):
        funny_text = utils.funny_message()
        acknowledgement = await ctx.respond(f"**{funny_text}**\nUpscaling the image for you!")
        # Send the request to the queue
        await core.queueHandler.add_request(funny_text, acknowledgement, "image_upscale", upscaler_name, scale,
                                            attached_image)
        print(f"Added request to queue: {upscaler_name}, {scale}")

    @commands.slash_command(description='Download a CivitAI model!', guild_only=True)
    @option(
        'model_url',
        str,
        description='The URL to download the model from.',
        required=True
    )
    @option(
        'model_name',
        str,
        description='The name of the model.',
        required=True
    )
    @option(
        'model_type',
        str,
        choices=['checkpoints', 'loras', 'vae', 'controlnets'],
        description='The type of model to download.',
        required=True
    )
    @option(
        "api_key",
        str,
        description="The API key to use for downloading the model.",
        required=False
    )
    async def download(self, ctx: discord.ApplicationContext,
                       model_url,
                       model_name,
                       model_type,
                       api_key: str = ""
                       ):
        print(ctx.user.roles)
        # get a funny message
        funny_text = utils.funny_message()

        acknowledgement = await ctx.respond(f"**{funny_text}**\nDownloading the model for you!")
        # Send the request to the queue
        await core.queueHandler.add_request(funny_text, acknowledgement, "model_download", model_url, model_name,
                                            model_type, api_key)
        print(f"Added request to queue: {model_url}, {model_name}, {model_type}")

    @commands.slash_command(description="Set default model settings", guild_only=True)
    @option(
        'model_name',
        str,
        description='The name of the model.',
        required=True,
        autocomplete=checkpoints_autocomplete
    )
    @option(
        'cfg_scale',
        int,
        min_value=1,
        max_value=10,
        description='Set the CFG scale for the model.',
        required=True
    )
    @option(
        'sampler_name',
        str,
        description='Set the sampler name for the model.',
        required=True,
        autocomplete=sampler_autocomplete
    )
    @option(
        'clip_skip',
        int,
        min_value=1,
        max_value=10,
        description='Set the recommended clip skip for the model.',
        required=True
    )
    async def update_settings(self, ctx: discord.ApplicationContext,
                              model_name,
                              cfg_scale,
                              sampler_name,
                              clip_skip
                              ):
        model_exists = False
        with open('core/resources/model_settings.csv', encoding='UTF-8') as csv_file:
            model_data = list(csv.reader(csv_file, delimiter='|'))
            for row in model_data:
                if row[0] == model_name:
                    model_exists = True
                    break
        if not model_exists:
            with open('core/resources/model_settings.csv', 'a', newline='', encoding='UTF-8') as csv_file:
                writer = csv.writer(csv_file, delimiter='|')
                writer.writerow([model_name, cfg_scale, sampler_name, clip_skip])
            await ctx.respond(
                f"Model settings for {model_name} have been set to: CFG Scale: {cfg_scale}, "
                f"Sampler Name: {sampler_name}, Clip Skip: {clip_skip}")
            csv_file.close()
        else:
            # If the model name exists, remove the row and add the new settings
            with open('core/resources/model_settings.csv', 'r', encoding='UTF-8') as csv_file:
                model_data = list(csv.reader(csv_file, delimiter='|'))
                for row in model_data:
                    if row[0] == model_name:
                        model_data.remove(row)
            with open('core/resources/model_settings.csv', 'w', newline='', encoding='UTF-8') as csv_file:
                writer = csv.writer(csv_file, delimiter='|')
                writer.writerows(model_data)
                writer.writerow([model_name, cfg_scale, sampler_name, clip_skip])
                await ctx.respond(
                    f"Model settings for {model_name} have been updated to: CFG Scale: {cfg_scale}, "
                    f"Sampler Name: {sampler_name}, Clip Skip: {clip_skip}")

            csv_file.close()


def setup(bot):
    bot.add_cog(GenerateCog(bot))
