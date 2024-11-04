from PIL import Image
import numpy as np
import random
import string
import requests
import sys

# Generate a strong password (random message)
def generate_strong_password(length=14):
    if length < 12:
        raise ValueError("Password length should be at least 12 characters")
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation
    password = [random.choice(lowercase), random.choice(uppercase), random.choice(digits), random.choice(symbols)]
    remaining_length = length - len(password)
    all_characters = lowercase + uppercase + digits + symbols
    password.extend(random.choice(all_characters) for _ in range(remaining_length))
    random.shuffle(password)
    return ''.join(password)

def embed_message_in_image(image_path, message):
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000' # Add termination sequence

        if len(binary_message) > img_array.size:
            raise ValueError("Image is too small to embed the message")

        index = 0
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                for k in range(img_array.shape[2]):
                    if index < len(binary_message):
                        img_array[i, j, k] = (img_array[i, j, k] & 254) | int(binary_message[index])
                        index += 1

        stego_img = Image.fromarray(img_array)
        output_path = 'encoded_image.png'   # Ensure this path is correct
        stego_img.save(output_path)
        return output_path

    except Exception as e:
        print(f"Error embedding message: {e}", file=sys.stderr)
        return None

    except Exception as e:
        print(f"Error embedding message: {e}")
        return None

# Extract the hidden message from an image
def extract_message_from_image(stego_image_path):
    try:
        img = Image.open(stego_image_path)
        img_array = np.array(img)

        binary_message = ''
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                for k in range(img_array.shape[2]):
                    binary_message += str(img_array[i, j, k] & 1)

                    if len(binary_message) % 8 == 0:
                        char = chr(int(binary_message[-8:], 2))
                        if char == '\0':  # Termination sequence found
                            return ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message)-8, 8))

    except Exception as e:
        print(f"Error extracting message: {e}")
        return None

# Get a random image from the internet
def get_random_image():
    try:
        width = random.randint(1000, 2000)
        height = random.randint(1000, 2000)
        image_id = random.randint(1, 1000)
        url = f'https://picsum.photos/id/{image_id}/{width}/{height}'

        response = requests.get(url)

        if response.status_code == 200:
            with open('random_image.jpg', 'wb') as file:
                file.write(response.content)
            return 'random_image.jpg'
        
    except Exception as e:
        print(f"Error downloading random image: {e}")
        return None

# Usage example:
# key = generate_strong_password()
# embed_message_in_image('random_image.jpg', key)
# extract_message_from_image('encoded_image.png')

if __name__ == "__main__":
    action = sys.argv[1]  # Action: encode or decode
    image_path = sys.argv[2]  # Image path

    if action == "encode":
        secret_key = sys.argv[3]  # Secret key or message
        output_image_path = embed_message_in_image(image_path, secret_key)
        
        if output_image_path:
            print(output_image_path)  # Return the path of the encoded image to Node.js server

    if action == "random":
        secret_key = sys.argv[3] # Secret key or message
        random_img_path = get_random_image() # Download a random image
        if random_img_path:
            output_image_path = embed_message_in_image(random_img_path, secret_key)
            if output_image_path:
                print(output_image_path) # Return path of encoded image back to Node.js server
            else:
                print("Error: Failed to embed message in image", file=sys.stderr)
        else:
            print("Error: Failed to download random image", file=sys.stderr)

    elif action == "decode":
        decoded_message = extract_message_from_image(image_path)
        
        if decoded_message:
            print(decoded_message)  # Return the decoded message to Node.js server