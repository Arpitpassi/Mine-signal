import cv2
import os
import numpy as np

def get_video_dimensions(video_path: str) -> tuple:
    """Get the dimensions of the input video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height

class VideoProcessor:
    ASCII_CHARS = "@%#*+=-:. "

    def __init__(self, width: int = 150):
        self.target_width = width

    def _resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """Resize the frame while maintaining aspect ratio."""
        height, width = frame.shape[:2]
        aspect_ratio = height / width
        new_height = int(self.target_width * aspect_ratio*0.65)
        return cv2.resize(frame, (self.target_width, new_height))

    def _convert_to_grayscale(self, frame: np.ndarray) -> np.ndarray:
        """Convert frame to grayscale."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def _map_pixels_to_ascii_chars(self, frame: np.ndarray) -> str:
        """Convert pixel values to ASCII characters."""
        # Normalize pixel values to ASCII character range
        pixel_indices = (frame // 32).astype(int)
        # Map pixel values to ASCII characters
        return ''.join(self.ASCII_CHARS[i] for i in pixel_indices.flatten())

    def _convert_frame_to_ascii(self, frame: np.ndarray) -> str:
        """Convert a single frame to ASCII art."""
        # Process the frame
        frame = self._resize_frame(frame)
        frame = self._convert_to_grayscale(frame)
        
        # Convert to ASCII with proper line breaks
        ascii_chars = self._map_pixels_to_ascii_chars(frame)
        lines = [ascii_chars[i:i + self.target_width] 
                for i in range(0, len(ascii_chars), self.target_width)]
        return '\n'.join(lines)

    def process_video(self, video_path: str, output_folder: str):
        """Process video file and generate ASCII frames."""
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to ASCII and save
            ascii_art = self._convert_frame_to_ascii(frame)
            output_path = os.path.join(output_folder, f"frame_{frame_count:06d}.txt")
            with open(output_path, "w") as f:
                f.write(ascii_art)
            
            frame_count += 1

        # Clean up
        cap.release()

def handle_video_processing(video_path: str, output_folder: str):
    """Handle the video processing workflow."""
    try:
        processor = VideoProcessor(width=100)
        processor.process_video(video_path, output_folder)
    except Exception as e:
        raise Exception(f"Video processing failed: {str(e)}")

if __name__ == "__main__":
    # Test code
    video_path = "test.mp4"
    output_folder = "frames"
    if os.path.exists(video_path):
        try:
            handle_video_processing(video_path, output_folder)
            print("Processing complete")
        except Exception as e:
            print(f"Error: {e}")