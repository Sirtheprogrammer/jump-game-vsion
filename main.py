import cv2
import pygame
from vision import FingerDetector
from game import Game

def main():
    # Initialize Vision
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    try:
        detector = FingerDetector()
    except Exception as e:
        print(f"Failed to init vision: {e}")
        return

    # Initialize Game
    game = Game()

    print("Starting Finger Jump Game...")
    print("Raise your INDEX FINGER to jump!")
    print("Press 'q' in the camera window or close the game window to quit.")

    while game.running:
        # 1. Vision Update
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        is_jumping, results = detector.process_frame(frame)
        
        # Visual feedback on camera feed
        if is_jumping:
            cv2.putText(frame, "JUMP!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if results.hand_landmarks:
             for hand_landmarks in results.hand_landmarks:
                for i, lm in enumerate(hand_landmarks):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if i == 8: # Index tip
                        cv2.circle(frame, (cx, cy), 8, (255, 0, 0), -1)

        cv2.imshow('Camera Feed (Finger to Jump)', frame)
        
        # 2. Game Update
        game.handle_input(is_jumping)
        game.update()
        game.render()
        game.step()
        
        # Check for quit in CV2 window
        if cv2.waitKey(1) == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
