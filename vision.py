import cv2
import mediapipe as mp
import numpy as np
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FingerDetector:
    def __init__(self, model_path='hand_landmarker.task'):
        try:
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=1,
                running_mode=vision.RunningMode.VIDEO)
            self.detector = vision.HandLandmarker.create_from_options(options)
        except Exception as e:
            print(f"Failed to initialize HandLandmarker: {e}")
            raise e

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Use current timestamp in ms
        timestamp_ms = int(time.time() * 1000)
        
        try:
            results = self.detector.detect_for_video(mp_image, timestamp_ms)
        except Exception as e:
            print(f"Detection error: {e}")
            return False, results

        is_jumping = False
        
        if results.hand_landmarks:
            # We only track the first hand
            landmarks = results.hand_landmarks[0]
            
            # Index finger tip is landmark 8
            # Index finger PIP (knuckle/joint) is landmark 6
            # In image coordinates, Y increases downwards.
            # So, if Tip Y < PIP Y, the finger is pointing UP.
            
            index_tip = landmarks[8]
            index_pip = landmarks[6]
            
            # Simple thresholding or relative position check
            # We want a clear "raised" state.
            if index_tip.y < index_pip.y:
                is_jumping = True
        
        return is_jumping, results
