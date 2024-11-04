import cv2
import numpy as np
import sys

def embed_message_in_frame(frame, message):
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'  # Add termination sequence
    
    bit_index = 0
    
    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(3):  # Iterate over color channels (BGR)
                if bit_index < len(binary_message):
                    frame[i,j,k] = (frame[i,j,k] & ~1) | int(binary_message[bit_index])
                    bit_index += 1
    
                if bit_index >= len(binary_message):
                    return frame
    return frame

def extract_message_from_frame(frame):
    binary_message = ''
    
    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(3):  # Iterate over color channels (BGR)
                binary_message += str(frame[i,j,k] & 1)

                if len(binary_message) % 8 == 0:
                    char = chr(int(binary_message[-8:], 2))
                    if char == '\0':  # Termination sequence found
                        return ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message)-8, 8))
    return ''

def encode_video(input_path, output_path, message):
    try:
        print("Starting video encoding...")
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {input_path}")
            return

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not out.isOpened():
            print(f"Error: Could not create output video file {output_path}")
            return

        ret, frame = cap.read()
        if ret:
            frame_with_message = embed_message_in_frame(frame, message)
            out.write(frame_with_message)
            print("Message embedded in first frame.")

        frame_count = 1
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            frame_count += 1

        print(f"Video encoding completed. Processed {frame_count} frames.")

    except Exception as e:
        print(f"An error occurred during video encoding: {str(e)}")
    finally:
        cap.release()
        out.release()

def decode_video(input_path):
    cap = cv2.VideoCapture(input_path)
    ret, frame = cap.read()
    if ret:
        message = extract_message_from_frame(frame)
        cap.release()
        return message
    cap.release()
    return ''

if __name__ == "__main__":
    action = sys.argv[1]
    input_path = sys.argv[2]

    if action == "encode":
        message = sys.argv[3]
        output_path = 'encoded_video.mp4'
        encode_video(input_path, output_path, message)
        print(output_path)
    elif action == "decode":
        message = decode_video(input_path)
        print(message)