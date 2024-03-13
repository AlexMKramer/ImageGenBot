from auto1111sdk import StableDiffusionPipeline, StableDiffusionXLPipeline, civit_download, download_realesrgan, \
    RealEsrganPipeline, ControlNetModel
import discord
import os
from PIL import Image
import time

app_directory = os.getcwd()


def txt2img(prompt,
            negative_prompt,
            model_path,
            num_images,
            height,
            width,
            steps,
            cfg_scale,
            sampler_name,
            clip_skip
            ):
    print(model_path)
    # check if the model path has 'sdxl' in it
    if "sdxl" in model_path:
        pipe = StableDiffusionXLPipeline(model_path, "--skip-torch-cuda-test --medvram", clip_skip)
        pipe.set_vae(os.path.join(os.getcwd(), "models/vae/sdxl.vae.safetensors"))
        pipe.weights_file = os.path.basename(model_path)
        print("Using SDXL")
    else:
        pipe = StableDiffusionPipeline(model_path, clip_skip)
    output = pipe.generate_txt2img(prompt=prompt,
                                   negative_prompt=negative_prompt,
                                   num_images=num_images,
                                   height=height,
                                   width=width,
                                   steps=steps,
                                   cfg_scale=cfg_scale,
                                   sampler_name=sampler_name,
                                   seed=-1
                                   )
    file_paths = []
    for i in range(num_images):
        # Save the output to a file in the output folder using the time and date as the file name
        file_name = f"ImageGenBot-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{i}.png"
        save_path = os.path.join(os.getcwd(), "output/")
        output[i].save(f"{save_path}{file_name}")
        print(f"Saved {file_name}")
        file_paths.append(f"{save_path}{file_name}")

    file_list = [discord.File(file_path) for file_path in file_paths]
    del pipe
    print("Finished generating text2images")
    return file_list


def img2img(prompt,
            negative_prompt,
            model_path,
            num_images,
            height,
            width,
            steps,
            cfg_scale,
            sampler_name,
            clip_skip,
            percent_of_original
            ):
    print(model_path)
    # check if the model path has 'sdxl' in it
    if "sdxl" in model_path:
        pipe = StableDiffusionXLPipeline(model_path, "--skip-torch-cuda-test --medvram", clip_skip)
        pipe.set_vae(os.path.join(os.getcwd(), "models/vae/sdxl.vae.safetensors"))
        pipe.weights_file = os.path.basename(model_path)
        print(f"Using SDXL {model_path} model to process the image")
    else:
        pipe = StableDiffusionPipeline(model_path, clip_skip)
        print(f"Using SD {model_path} model to process the image")
    output = pipe.generate_img2img(prompt=prompt,
                                   init_image=Image.open("attached_image.png"),
                                   negative_prompt=negative_prompt,
                                   num_images=num_images,
                                   height=height,
                                   width=width,
                                   steps=steps,
                                   cfg_scale=cfg_scale,
                                   sampler_name=sampler_name,
                                   seed=-1,
                                   denoising_strength=(1.0 - (percent_of_original / 100))
                                   )
    file_paths = []
    for i in range(num_images):
        # Save the output to a file in the output folder using the time and date as the file name
        file_name = f"ImageGenBot-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{i}.png"
        save_path = os.path.join(os.getcwd(), "output/")
        output[i].save(f"{save_path}{file_name}")
        print(f"Saved {file_name}")
        file_paths.append(f"{save_path}{file_name}")

    file_list = [discord.File(file_path) for file_path in file_paths]
    pipe.set_vae(None)
    del pipe
    print("Finished generating image2images.")
    return file_list


def controlnet(prompt,
               negative_prompt,
               model_path,
               num_images,
               height,
               width,
               steps,
               cfg_scale,
               sampler_name,
               clip_skip,
               controlnet_name
               ):
    print(model_path)
    # If a controlnet is specified, run the image through the controlnet first
    controlnet_path = os.path.join(os.getcwd(), "models/controlnets/" + controlnet_name)
    controlnet_model = ControlNetModel(model_path=controlnet_path, image="attached_image.png")
    pipe = StableDiffusionPipeline(model_path, controlnet=controlnet_model, clip_skip=clip_skip)
    print(f"Using {controlnet} controlnet to process the image")
    output = pipe.generate_txt2img(prompt=prompt,
                                   negative_prompt=negative_prompt,
                                   num_images=num_images,
                                   height=height,
                                   width=width,
                                   steps=steps,
                                   cfg_scale=cfg_scale,
                                   sampler_name=sampler_name,
                                   seed=-1
                                   )
    file_paths = []
    for i in range(num_images):
        # Save the output to a file in the output folder using the time and date as the file name
        file_name = f"ImageGenBot-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{i}.png"
        save_path = os.path.join(os.getcwd(), "output/")
        output[i].save(f"{save_path}{file_name}")
        print(f"Saved {file_name}")
        file_paths.append(f"{save_path}{file_name}")

    file_list = [discord.File(file_path) for file_path in file_paths]
    pipe.set_vae(None)
    del pipe
    print("Finished generating controlnet images.")
    return file_list


def image_upscale(model_name, scale):
    # Get the model path
    model_path = os.path.join(os.getcwd(), "models/upscalers/" + model_name + ".pth")
    # Check if the model exists and download it if it doesn't
    if not os.path.exists(model_path):
        print(f"Downloading {model_name} model")
        download_realesrgan(model_name, model_path)
    print(f"Using {model_name} model to upscale the image")

    upscaler = RealEsrganPipeline(model_name, model_path)
    output = upscaler.upscale(img=Image.open("attached_image.png"),
                              scale=scale)

    # Save the output to a file in the output folder using the time and date as the file name
    file_name = f"ImageGenBot-{time.strftime('%Y-%m-%d-%H-%M-%S')}-upscaled.png"
    save_path = os.path.join(os.getcwd(), "output/")
    output.save(f"{save_path}{file_name}")
    file_list = [discord.File(f"{save_path}{file_name}")]

    print(f"Finished upscaling.  File saved {file_name}")
    del upscaler
    return file_list


def model_download(model_url, model_name, model_type, api_key):
    # Download the model into the Models folder
    try:
        download_folder = os.path.join(os.getcwd(), "models/" + model_type + "/")
        os.chdir(download_folder)
        if api_key:
            civit_download(model_url, model_name, api_key)
        else:
            civit_download(model_url, model_name)
        os.chdir(os.path.join(os.getcwd(), "../.."))
        print(f"Downloaded {model_name} model")
        return True
    except Exception as e:
        print(e)
        if os.getcwd() != app_directory:
            os.chdir(app_directory)
        return e
