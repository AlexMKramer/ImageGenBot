import core.auto1111
import asyncio
from discord.ext import commands, tasks
from PIL import Image
import io

command_queue = asyncio.Queue()
queue_processing = False


height_width_option = [
    {"height": 1024, "width": 1024, "aspect_ratio": 1},
    {"height": 1152, "width": 896, "aspect_ratio": 1.2857142857142858},
    {"height": 896, "width": 1152, "aspect_ratio": 0.7777777777777778},
    {"height": 1216, "width": 832, "aspect_ratio": 1.4615384615384615},
    {"height": 832, "width": 1216, "aspect_ratio": 0.6842105263157895},
    {"height": 1344, "width": 768, "aspect_ratio": 1.75},
    {"height": 768, "width": 1344, "aspect_ratio": 0.5714285714285714},
    {"height": 1536, "width": 640, "aspect_ratio": 2.4},
    {"height": 640, "width": 1536, "aspect_ratio": 0.4166666666666667},
]


# Use the command_queue from the main file to add requests to the queue
async def add_request(funny_text, acknowledgement, gen_type: str, *args):
    await command_queue.put((funny_text, acknowledgement, gen_type, args))
    # Check the queue placement and update the acknowledgement message
    queue_spot = check_queue_placement()
    if queue_spot > 1:
        await acknowledgement.edit_original_response(content=f'**{funny_text}**\nYour request is number {queue_spot} in the queue.')
    elif queue_spot == 1:
        await acknowledgement.edit_original_response(content=f'**{funny_text}**\nYour request is next!')
    else:
        await acknowledgement.edit_original_response(content=f'**{funny_text}**\nYour request is being processed!')
    # Print User's name, the type of request added to the queue, and the queue size
    print(f'Added a {gen_type} request to the queue.  Queue size:{command_queue.qsize()}')


# Function to check the queue size
def check_queue_placement():
    # Check if the queue has something in it
    if not command_queue.empty():
        # Check if the queue is processing
        if queue_processing:
            queue_spot = command_queue.qsize()
            return queue_spot
        else:
            queue_spot = command_queue.qsize() - 1
            return queue_spot
    else:
        if queue_processing:
            return 1
        else:
            return 0


# Get all args from the processing command and formulate a message to send to the user
def form_message(funny_text, message_args):
    message = f"**{funny_text}**\n"
    for key, value in message_args.items():
        if not value != "":
            # skip empty values
            continue
        else:
            message += f"**{key}:** {value}\n"
    return message


@tasks.loop(seconds=1)
async def queue_loop():
    global queue_processing
    try:
        if not command_queue.empty():
            request = await command_queue.get()
            queue_processing = True
            funny_text, acknowledgement, gen_type, args = request
            await acknowledgement.edit_original_response(content=f'**{funny_text}**\nYour request is being processed!')
            loop = asyncio.get_event_loop()
            if gen_type == "txt2img":
                print(args)
                prompt, negative_prompt, model_path, num_images, height, width, steps, cfg_scale, sampler_name, clip_skip = args
                file_list = await loop.run_in_executor(None, core.auto1111.txt2img, prompt, negative_prompt, model_path,
                                                       num_images, height, width, steps, cfg_scale, sampler_name,
                                                       clip_skip)
                # get model name from model path
                model_name = model_path.split("/")[-1]
                model_name = model_name.split(".")[0]
                message_args = {"Prompt": prompt, "Negative Prompt": negative_prompt, "Model Name": model_name,
                                "Height": height, "Width": width, "Steps": steps, "CFG Scale": cfg_scale,
                                "Sampler Name": sampler_name}
                message = form_message(funny_text, message_args)

            elif gen_type == "img2img":
                print(args)
                (prompt, negative_prompt, model_path, num_images, steps, cfg_scale, sampler_name,
                 clip_skip, attached_image, percent_of_original) = args

                # save the attached image to a file
                attached_image = io.BytesIO(await attached_image.read())
                attached_image = Image.open(attached_image)
                width, height = attached_image.size
                aspect_ratio = height / width
                print(f"Image aspect ratio: {aspect_ratio}")

                closest_option = min(height_width_option, key=lambda option: abs(option["aspect_ratio"] - aspect_ratio))

                width = closest_option["width"]
                height = closest_option["height"]

                attached_image.resize((width, height), Image.LANCZOS)
                attached_image.save("attached_image.png")

                file_list = await loop.run_in_executor(None, core.auto1111.img2img, prompt, negative_prompt, model_path,
                                                       num_images, height, width, steps, cfg_scale, sampler_name,
                                                       clip_skip, percent_of_original)
                # get model name from model path
                model_name = model_path.split("/")[-1]
                model_name = model_name.split(".")[0]
                message_args = {"Prompt": prompt, "Negative Prompt": negative_prompt, "Model Name": model_name,
                                "Height": height, "Width": width, "Steps": steps, "CFG Scale": cfg_scale,
                                "Sampler Name": sampler_name, "Percent of Original Image": percent_of_original}
                message = form_message(funny_text, message_args)

            elif gen_type == 'image_upscale':
                print(args)
                (model_name, scale, attached_image) = args
                # save the attached image to a file
                attached_image = io.BytesIO(await attached_image.read())
                attached_image = Image.open(attached_image)
                attached_image.save("attached_image.png")

                file_list = await loop.run_in_executor(None, core.auto1111.image_upscale, model_name, scale)
                message_args = {"Model Name": model_name, "Scale": scale}
                message = form_message(funny_text, message_args)

            elif gen_type == "model_download":
                model_url, model_name, model_type, api_key = args
                file_status = await loop.run_in_executor(None, core.auto1111.model_download, model_url, model_name,
                                                         model_type, api_key)
                if file_status is True:
                    message = (f"Model {model_name} downloaded successfully!\n Run /update_settings to set the CFG and "
                               f"Sampler")
                    await acknowledgement.edit_original_response(content=message)
                    print(f"Model {model_name} downloaded successfully!")
                    queue_processing = False
                    return
                else:
                    print(f"Model download failed")
                    raise ValueError(f"Model download failed. Error: {file_status}")
            else:
                raise ValueError("Invalid command type")
            await acknowledgement.edit_original_response(content=message, files=file_list)
            queue_processing = False
            del file_list, acknowledgement
    except Exception as e:
        error_message = "I'm sorry, I couldn't generate the images for you.\n" + str(e)
        print(e)
        await acknowledgement.edit_original_response(content=error_message)
        queue_processing = False
        del acknowledgement
        # If there is an error, clear the item from the queue and continue
        command_queue.task_done()

