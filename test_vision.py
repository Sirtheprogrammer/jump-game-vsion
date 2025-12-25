import cv2
import mediapipe as mp
from vision import FingerDetector

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    try:
        detector = FingerDetector()
    except Exception as e:
        print(f"Failed to load detector: {e}")
        return

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        is_jumping, results = detector.process_frame(frame)

        if is_jumping:
            cv2.putText(frame, "JUMP!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Finger Raised", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw landmarks if available
        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                for i, lm in enumerate(hand_landmarks):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # Draw Index Finger Tip (8)
                    if i == 8:
                        cv2.circle(frame, (cx, cy), 10, (255, 0, 0), -1)
                    else:
                        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        cv2.imshow('Finger Detection Test', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
