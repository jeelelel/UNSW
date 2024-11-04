import numpy as np
from scipy.io.wavfile import read, write
import sys
import random
import tempfile
from pydub.generators import Sine, WhiteNoise
from pydub import AudioSegment

# Encode a message into an audio file
def encode_audio_with_message(audio_file, message):
    sample_rate, audio_data = read(audio_file)
    
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'  # Add termination sequence
    
    if len(binary_message) > len(audio_data):
        raise ValueError("Message too long for the audio file")
    
    audio_data = audio_data.astype(np.int16)
    
    for i in range(len(binary_message)):
        audio_data[i] = (audio_data[i] & 0xFFFE) | int(binary_message[i])
    
    encoded_audio_file = 'encoded_audio.wav'
    write(encoded_audio_file, sample_rate, audio_data)
    
    return encoded_audio_file

# Decode the hidden message from an audio file
def decode_audio_message(audio_file):
    sample_rate, audio_data = read(audio_file)
    
    binary_message = ''.join(str(sample & 1) for sample in audio_data)
    
    delimiter_index = binary_message.find('00000000')  # Find termination sequence
    
    if delimiter_index == -1:
        return "No hidden message found"
    
    message = ''
    
    for i in range(0, delimiter_index, 8):
        byte = binary_message[i:i+8]
        message += chr(int(byte, 2))
    
    return message

# Generate a random melody-like audio file
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

if __name__ == "__main__":
    action = sys.argv[1]  # Action: encode or decode or generate_random_audio
    if action == "encode":
        audio_path = sys.argv[2]
        secret_key = sys.argv[3]  # Secret key or message
        output_audio_path = encode_audio_with_message(audio_path, secret_key)
        
        if output_audio_path:
            print(output_audio_path)  # Return the path of the encoded audio to Node.js server

    elif action == "decode":
        audio_path = sys.argv[2]
        decoded_message = decode_audio_message(audio_path)
        
        if decoded_message:
            print(decoded_message)  # Return the decoded message to Node.js server

    elif action == "generate_random_audio":
        generated_audio_path = generate_music_like_audio()
        print(generated_audio_path)  # Return the path of the generated random audio to Node.js server