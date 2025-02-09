# -*- coding: utf-8 -*-
"""SomethingAweSome.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZSSUiNyc3-x0BAm6CseGVl0WGdBuxz-D

# Steganography project app

## Photo Steganography Project
"""
import sys
import matplotlib.pyplot as plt
import requests
import random
import string
import numpy as np
from PIL import Image

def generate_strong_password(length=14):
    if length < 12:
        raise ValueError("Password length should be at least 12 characters")

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation

    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(symbols)
    ]

    remaining_length = length - len(password)
    all_characters = lowercase + uppercase + digits + symbols
    password.extend(random.choice(all_characters) for _ in range(remaining_length))

    random.shuffle(password)

    return ''.join(password)

def embed_password(image_path, password):
    img = Image.open(image_path)
    img_array = np.array(img)

    # Add a termination sequence (e.g., '\0') to mark the end of the password
    password += '\0'
    binary_password = ''.join(format(ord(char), '08b') for char in password)

    if len(binary_password) > img_array.size:
        raise ValueError("Image is too small to embed the password")

    index = 0
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(img_array.shape[2]):
                if index < len(binary_password):
                    img_array[i, j, k] = (img_array[i, j, k] & 254) | int(binary_password[index])
                    index += 1
                else:
                    break
            if index >= len(binary_password):
                break
        if index >= len(binary_password):
            break

    stego_img = Image.fromarray(img_array)
    stego_img.save('stego_image.png')
    return 'stego_image.png'

def extract_password(stego_image_path):
    img = Image.open(stego_image_path)
    img_array = np.array(img)

    binary_password = ''
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(img_array.shape[2]):
                binary_password += str(img_array[i, j, k] & 1)
                if len(binary_password) % 8 == 0:
                    char = chr(int(binary_password[-8:], 2))
                    if char == '\0':
                        # Found termination sequence, stop extraction
                        return ''.join(chr(int(binary_password[i:i+8], 2)) for i in range(0, len(binary_password)-8, 8))

    raise ValueError("No termination sequence found. Password extraction failed.")

def get_random_image():
    width = random.randint(1000, 2000)
    height = random.randint(1000, 2000)
    image_id = random.randint(1, 1000)
    url = f'https://picsum.photos/id/{image_id}/{width}/{height}'

    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

def save_random_image(filename='random_image.jpg'):
    image_data = get_random_image()
    if image_data:
        with open(filename, 'wb') as file:
            file.write(image_data)
        print(f"Random image has been saved as '{filename}'")
    else:
        print("Failed to download the image")

"""## Steganography on Audio"""

import numpy as np
from scipy.io.wavfile import read, write
import tempfile
import random
import string

from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise

def generate_music_like_audio(duration=5):
    # Generate a simple melody-like sequence
    audio = AudioSegment.silent(duration=duration * 1000)

    # Define a pentatonic scale (C4, D4, E4, G4, A4)
    frequencies = [261.63, 293.66, 329.63, 392.00, 440.00]

    for _ in range(10):  # Generate 10 random notes
        freq = random.choice(frequencies)
        note_duration = random.randint(200, 500)  # Note duration between 200ms and 500ms
        tone = Sine(freq).to_audio_segment(duration=note_duration)
        position = random.randint(0, len(audio) - len(tone))
        audio = audio.overlay(tone, position=position)

    # Add some white noise for texture
    noise = WhiteNoise().to_audio_segment(duration=len(audio))
    audio = audio.overlay(noise, gain_during_overlay=-30)

    # Export to a temporary WAV file
    temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    audio.export(temp_wav_file.name, format="wav")
    return temp_wav_file.name

def encode_audio_with_message(audio_file, message):
    sample_rate, audio_data = read(audio_file)
    audio_data = audio_data.astype(np.int16)

    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'

    if len(binary_message) > len(audio_data):
        raise ValueError("Message too long for the audio file")

    for i in range(len(binary_message)):
        audio_data[i] = (audio_data[i] & 0xFFFE) | int(binary_message[i])

    encoded_audio_file = 'encoded_audio.wav'
    write(encoded_audio_file, sample_rate, audio_data)
    return encoded_audio_file

def decode_audio_message(audio_file):
    sample_rate, audio_data = read(audio_file)
    audio_data = audio_data.astype(np.int16)

    binary_message = ''.join(str(sample & 1) for sample in audio_data)

    delimiter_index = binary_message.find('00000000')
    if delimiter_index == -1:
        return "No hidden message found"

    message = ''
    for i in range(0, delimiter_index, 8):
        byte = binary_message[i:i+8]
        message += chr(int(byte, 2))

    return message

"""## Video Steganography Project"""

import requests
from bs4 import BeautifulSoup
import random
import os
import cv2
import numpy as np
import random
import string

def get_random_dog_video():
    api_url = "https://random.dog/woof.json"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if data['url'].endswith(('.mp4', '.webm')):
            return {
                'title': 'random_dog_video',
                'download_url': data['url']
            }
        else:
            # If it's not a video, try again
            return get_random_dog_video()
    except requests.RequestException as e:
        print(f"Error fetching video: {e}")
        return None

def download_video(video_info, output_dir='.'):
    if not video_info:
        print("No video information available.")
        return None

    try:
        response = requests.get(video_info['download_url'], stream=True)
        response.raise_for_status()

        # Get the file extension from the URL
        file_extension = os.path.splitext(video_info['download_url'])[1]
        filename = f"{video_info['title']}{file_extension}"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded: {filename}")
        return filepath
    except requests.RequestException as e:
        print(f"Error downloading video: {e}")
        return None

def check_message_fits(frame, message):
    """Check if the message can fit within the given frame."""
    # Combine markers with message
    message_with_marker = FRAME_MARKER + message + END_MARKER

    # Convert to binary bits
    message_bits = ''.join([format(byte, '08b') for byte in message_with_marker])

    # Calculate available capacity
    max_capacity = frame.shape[0] * frame.shape[1] * 3  # 3 bits per pixel (BGR)

    if len(message_bits) > max_capacity:
        raise ValueError(f"Message too large to fit in this frame. "
                         f"Max capacity: {max_capacity} bits, "
                         f"Message size: {len(message_bits)} bits.")
    else:
        print(f"Message fits within the frame. Message size: {len(message_bits)} bits.")

def debug_frame_bits(frame):
    """Print out some LSBs of a few pixels for debugging."""
    for i in range(5):  # Print first 5 pixels' LSBs
        for j in range(5):
            print(f"Pixel ({i},{j}): {[frame[i, j, k] & 1 for k in range(3)]}")

def get_frame_count(video_path):
    """Returns the total number of frames in a video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return 0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frame_count

#fixed
# Constants for markers
FRAME_MARKER = b'#FRM_'
END_MARKER = b'_EOM#'

def is_valid_video(file_path):
    """Check if a video file exists and can be opened by OpenCV."""
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file '{file_path}'.")
        return False

    ret, frame = cap.read()
    cap.release()

    if ret and frame is not None:
        print(f"Valid video with frame shape: {frame.shape}")
        return True
    else:
        print(f"Error: Could not read a valid frame from '{file_path}'.")
        return False

def generate_random_password(length=8):
    """Generate a random password containing letters, digits, and punctuation."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password  # Return as string

def check_message_fits(frame, message):
    """Check if the message can fit within the given frame."""
    message_with_marker = FRAME_MARKER + message + END_MARKER
    message_bits = ''.join([format(byte, '08b') for byte in message_with_marker])

    max_capacity = frame.shape[0] * frame.shape[1] * 3  # 3 bits per pixel (BGR)

    if len(message_bits) > max_capacity:
        raise ValueError(f"Message too large to fit in this frame. "
                         f"Max capacity: {max_capacity} bits, "
                         f"Message size: {len(message_bits)} bits.")

def embed_message_in_frame(frame, message):
    """Embed a binary message into the least significant bits (LSBs) of a video frame."""
    # Combine markers with message
    message_with_marker = FRAME_MARKER + message + END_MARKER

    # Convert to binary bits
    message_bits = ''.join([format(byte, '08b') for byte in message_with_marker])

    bit_index = 0
    total_bits = len(message_bits)

    # Ensure we have enough space in the frame for the entire message
    max_capacity = frame.shape[0] * frame.shape[1] * 3  # 3 channels per pixel (BGR)

    if total_bits > max_capacity:
        raise ValueError(f"Message too large to fit in this frame. Max capacity: {max_capacity} bits.")

    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(3):  # Iterate over color channels (BGR)
                if bit_index < total_bits:
                    # Embed bit into LSB of pixel value
                    frame[i, j, k] = (frame[i, j, k] & 0xFE) | int(message_bits[bit_index])
                    bit_index += 1
                else:
                    return frame  # Stop embedding once all bits are embedded
    return frame

def extract_message_from_frame(frame):
    """Extract a binary message from the least significant bits (LSBs) of a video frame."""
    extracted_bits = []

    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(3):  # Iterate over color channels (BGR)
                extracted_bits.append(str(frame[i, j, k] & 1))  # Extract LSB

    # Convert bits to bytes
    bit_string = ''.join(extracted_bits)

    extracted_bytes = bytes(int(bit_string[i:i+8], 2) for i in range(0, len(bit_string), 8))

    return extracted_bytes

def find_and_decode_message(extracted_bytes):
    """Find and decode the hidden message between FRAME_MARKER and END_MARKER."""
    try:
        start_index = extracted_bytes.index(FRAME_MARKER)
        end_index = extracted_bytes.index(END_MARKER, start_index) + len(END_MARKER)

        # Extract and decode the message between markers
        hidden_message = extracted_bytes[start_index + len(FRAME_MARKER):end_index - len(END_MARKER)].decode('utf-8')
        return hidden_message
    except ValueError as e:
        print(f"Error: Could not find message markers. {e}")
        return None

def write_video_with_embedded_message(input_video_path, output_video_path, message):
    """Embed a message into the first keyframe of a video and save it to a new file."""

    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        print("Error: Could not open input video.")
        return

    ret, frame = cap.read()

    if not ret or frame is None:
        print("Error: Could not read a valid frame from input video.")
        return

    try:
        check_message_fits(frame, message)  # Ensure that our secret fits

        # Embed message into the first keyframe
        frame_with_message = embed_message_in_frame(frame.copy(), message)

        # Use FFV1 lossless codec for output video to avoid compression artifacts
        fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (frame.shape[1], frame.shape[0]))

        out.write(frame_with_message)  # Write modified first frame

        while cap.isOpened():
            ret, next_frame = cap.read()
            if not ret:
                break
            out.write(next_frame)

        out.release()

    except ValueError as e:
        print(f"Error embedding message: {e}")

    finally:
        cap.release()

def extract_message_from_video(video_path):
    """Extract a hidden message from the first keyframe of a video."""

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    ret, frame = cap.read()

    if ret and frame is not None:

        extracted_bytes = extract_message_from_frame(frame)

        hidden_message = find_and_decode_message(extracted_bytes)

        if hidden_message:
            print(f"Extracted message: {hidden_message}")
            return hidden_message
        else:
            print("No valid message found.")
            return None

    else:
        print("Error: Could not read a valid frame from video.")

    cap.release()

# Step 1: Validate that the downloaded file is indeed a valid video.
if is_valid_video(downloaded_file):
    # Convert the password to bytes before embedding it into the video
    secret_password_bytes = video_key.encode('utf-8')

    write_video_with_embedded_message(downloaded_file, 'output_video.avi', secret_password_bytes)

    extract_message_from_video('output_video.avi')

video_key