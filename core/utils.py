import csv
import os
import random

height_width_option = [
    {"height": 512, "width": 512, "aspect_ratio": 1},
    {"height": 768, "width": 768, "aspect_ratio": 1},
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


sampler_options = [
    'DPM++ 2M Karras',
    'DPM++ SDE Karras',
    'DPM++ 2M SDE Exponential',
    'DPM++ 2M SDE Karras',
    'Euler a',
    'Euler',
    'LMS',
    'Heun',
    'DPM2',
    'DPM2 a',
    'DPM++ 2S a',
    'DPM++ 2M',
    'DPM++ SDE',
    'DPM++ 2M SDE',
    'DPM++ 2M SDE Heun',
    'DPM++ 2M SDE Heun Karras',
    'DPM++ 2M SDE Heun Exponential',
    'DPM++ 3M SDE',
    'DPM++ 3M SDE Karras',
    'DPM++ 3M SDE Exponential',
    'DPM fast',
    'DPM adaptive',
    'LMS Karras',
    'DPM2 Karras',
    'DPM2 a Karras',
    'DPM++ 2S a Karras'
    ]

wait_message = []


def funny_message():
    with open('core/resources/messages.csv', encoding='UTF-8') as csv_file:
        message_data = list(csv.reader(csv_file, delimiter='|'))
        for row in message_data:
            wait_message.append(row[0])
    wait_message_count = len(wait_message) - 1
    text = wait_message[random.randint(0, wait_message_count)]
    return text


def get_checkpoints():
    models_folder_path = os.path.join(os.getcwd(), "models/")
    for dirpath, dirnames, filenames in os.walk(models_folder_path):
        subfolder_name = 'checkpoints'
        # Check if the target subfolder is in the current directory
        if subfolder_name in dirnames:
            subfolder_path = os.path.join(dirpath, subfolder_name)

            # List files within the target subfolder
            subfolder_files = [file for file in os.listdir(subfolder_path) if
                               os.path.isfile(os.path.join(subfolder_path, file))]
            matching_files = [os.path.splitext(checkpoints)[0] for checkpoints in subfolder_files]
            # remove place_checkpoints_here.txt file from the list
            if 'place_checkpoints_here' in matching_files:
                matching_files.remove('place_checkpoints_here')
            return sorted(matching_files)
    # If the target subfolder is not found
    return []


# Search lora folder
def get_loras():
    models_folder_path = os.path.join(os.getcwd(), "models/")
    for dirpath, dirnames, filenames in os.walk(models_folder_path):
        subfolder_name = 'loras'
        # Check if the target subfolder is in the current directory
        if subfolder_name in dirnames:
            subfolder_path = os.path.join(dirpath, subfolder_name)

            # List files within the target subfolder
            subfolder_files = [file for file in os.listdir(subfolder_path) if
                               os.path.isfile(os.path.join(subfolder_path, file))]
            matching_files = [os.path.splitext(loras)[0] for loras in subfolder_files]
            # remove place_loras_here.txt file from the list
            if 'place_loras_here' in matching_files:
                matching_files.remove('place_loras_here')
            return sorted(matching_files)
    # If the target subfolder is not found
    return []


# Search controlnets folder
def get_controlnets():
    models_folder_path = os.path.join(os.getcwd(), "models/")
    for dirpath, dirnames, filenames in os.walk(models_folder_path):
        subfolder_name = 'controlnets'
        # Check if the target subfolder is in the current directory
        if subfolder_name in dirnames:
            subfolder_path = os.path.join(dirpath, subfolder_name)

            # List files within the target subfolder
            subfolder_files = [file for file in os.listdir(subfolder_path) if
                               os.path.isfile(os.path.join(subfolder_path, file))]
            matching_files = [os.path.splitext(controlnets)[0] for controlnets in subfolder_files]
            # remove place_loras_here.txt file from the list
            if 'place_controlnets_here' in matching_files:
                matching_files.remove('place_controlnets_here')
            return sorted(matching_files)
    # If the target subfolder is not found
    return []


def get_model_settings(model_name):
    # Get the default settings for the model chosen
    with open('core/resources/model_settings.csv', encoding='UTF-8') as csv_file:
        model_data = list(csv.reader(csv_file, delimiter='|'))
        # Check if the model name exists in the settings file
        model_found = False
        for row in model_data:
            if row[0] == model_name:
                # Check that there are no empty values in the row for rows 1, 2, and 3
                if row[1] is None:
                    cfg_scale = 2
                else:
                    cfg_scale = int(row[1])
                if row[2] is None:
                    sampler_name = "DPM++ 2M Karras"
                else:
                    sampler_name = row[2]
                if row[3] is None:
                    clip_skip = 1
                else:
                    clip_skip = row[3]
                csv_file.close()
                model_found = True
                break
        if not model_found:
            csv_file.close()
            # If the model name does not exist in the settings file, write the default settings to the file
            with open('core/resources/model_settings.csv', 'a', newline='', encoding='UTF-8') as csv_file_append:
                writer = csv.writer(csv_file_append, delimiter='|')
                writer.writerow([model_name, '2', 'DPM++ 2M Karras', '1'])
            csv_file_append.close()
            cfg_scale = 2
            sampler_name = "DPM++ 2M Karras"
            clip_skip = 1
        return cfg_scale, sampler_name, clip_skip
