import cv2
import os

def capture_specific_times(video_path, output_folder, start_minute=1, start_second=15, interval_minutes=1):
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print("Error: Could not open video.")
        return

    # Get video properties
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_seconds = total_frames / fps

    print(f"Video Duration: {duration_seconds:.2f} seconds")

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Calculate capture times (in seconds)
    capture_times = []
    current_minute = start_minute
    while True:
        capture_time = (current_minute * 60) + start_second
        if capture_time > duration_seconds:
            break
        capture_times.append(capture_time)
        current_minute += interval_minutes

    print(f"Capture Times (in seconds): {capture_times}")

    # Start capturing
    for idx, capture_time in enumerate(capture_times):
        frame_number = int(capture_time * fps)
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = video.read()
        
        if ret:
            output_path = os.path.join(output_folder, f"frame_{idx+1:03d}.jpg")
            cv2.imwrite(output_path, frame)
            print(f"Captured {output_path} at {capture_time:.2f} seconds")
        else:
            print(f"Failed to capture at {capture_time:.2f} seconds")

    video.release()
    print("Done capturing frames.")

if __name__ == "__main__":
    video_file = "2.mp4"  
    output_dir = "2"
    capture_specific_times(video_file, output_dir)
