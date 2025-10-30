"""
Modified SmartPhysio Demo Assistant with Web Integration
Integrates with Flask web application for data persistence and analysis
"""

import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import pyttsx3
import threading
import queue
import time
import requests
import json

class SmartPhysioWebIntegrated:
    def __init__(self, exercise, session_mode, api_url='http://localhost:5000/api'):
        self.exercise = exercise.lower()
        self.session_mode = session_mode
        self.api_url = api_url
        self.session_id = None
        
        # Initialize MediaPipe
        self.mppose = mp.solutions.pose
        self.pose = self.mppose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mpdrawing = mp.solutions.drawing_utils
        self.current_ex = self.exercise
        self.FPS = 30
        
        # Audio setup
        self.audio_queue = queue.Queue()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 1.0)
        self.audio_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.audio_thread.start()
        
        # Session control
        self.session_active = False
        self.start_time = time.time()
        self.last_status_message = ""
        self.last_key_press_time = 0
        
        # Perfect thresholds
        self.squat_perfect_angle = 90
        self.abd_perfect_angle = 150
        self.eflex_perfect_angle = 40
        self.hflex_perfect_angle = 100
        self.wext_perfect_angle = 120
        
        # Correct/Rest angles
        self.down_knee_angle = 110
        self.up_knee_angle = 160
        self.abd_down_angle = 30
        self.abd_up_angle = 90
        self.abd_max_angle = 170
        self.eflex_straight_angle = 160
        self.eflex_bent_angle = 70
        self.hflex_straight_angle = 165
        self.hflex_bent_angle = 120
        self.wext_straight_angle = 165
        self.wext_bent_angle = 135
        
        # Exercise states
        self.exercises = {
            "squat": self._get_state(),
            "abduction": self._get_state(),
            "elbow": self._get_state(),
            "hipflex": self._get_state(),
            "wristext": self._get_state()
        }
        
        if self.session_mode == "assisted":
            self.last_status_message = "SESSION PAUSED"
        
        # Create session in database
        self._create_session()
    
    def _create_session(self):
        """Create a new session in the database"""
        try:
            response = requests.post(f'{self.api_url}/sessions', json={
                'exercise_type': self.exercise,
                'session_mode': self.session_mode
            })
            if response.status_code == 200:
                self.session_id = response.json()['session_id']
                print(f"Session created with ID: {self.session_id}")
            else:
                print("Failed to create session in database")
        except Exception as e:
            print(f"Error creating session: {e}")
    
    def _log_rep_to_db(self, rep_number, score, perfect_frames, standard_frames, tracked_side, best_angle):
        """Log a completed rep to the database"""
        if not self.session_id:
            return
        
        try:
            requests.post(f'{self.api_url}/reps', json={
                'session_id': self.session_id,
                'rep_number': rep_number,
                'score': float(score),
                'perfect_frames': int(perfect_frames),
                'standard_frames': int(standard_frames),
                'tracked_side': tracked_side,
                'best_angle': float(best_angle)
            })
        except Exception as e:
            print(f"Error logging rep: {e}")
    
    def _log_form_event(self, event_type, angle, form_status, feedback_message=""):
        """Log form events to the database"""
        if not self.session_id:
            return
        
        try:
            requests.post(f'{self.api_url}/form_events', json={
                'session_id': self.session_id,
                'event_type': event_type,
                'angle': float(angle),
                'form_status': form_status,
                'feedback_message': feedback_message
            })
        except Exception as e:
            print(f"Error logging form event: {e}")
    
    def _update_session(self, total_reps, average_score, duration_seconds):
        """Update session data in database"""
        if not self.session_id:
            return
        
        try:
            requests.put(f'{self.api_url}/sessions/{self.session_id}', json={
                'total_reps': int(total_reps),
                'average_score': float(average_score),
                'duration_seconds': int(duration_seconds),
                'status': 'completed'
            })
            print("Session data updated successfully")
        except Exception as e:
            print(f"Error updating session: {e}")
    
    def _get_state(self):
        """Returns a clean state dictionary for an exercise"""
        return {
            "repcount": 0, "phase": "none", "ready": False,
            "start_frames_needed": 12, "start_frames_counter": 0,
            "rep_scores": [], "rep_start_frame": 0,
            "current_rep_perfect_frames": 0,
            "current_rep_standard_frames": 0,
            "error_persistence_counter": 0, "audio_lock_perfect": False,
            "audio_lock_correct": False, "frame_counter": 0,
            "session_data": [], "feedback": "", "tracked_side": "NONE",
            "current_rep_best_angle": 180 if self.current_ex != "abduction" else 0,
            "rest_persistence_counter": 0,
            "in_incorrect_attempt": False,
            "last_stopped_frame": 0,
            "session_ended_for_ex": False,
        }
    
    def _audio_worker(self):
        while True:
            message = self.audio_queue.get()
            if message is None:
                break
            try:
                self.engine.say(message)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Audio worker error: {e}")
    
    def play_audio(self, message):
        print(f"AUDIO CUE: {message}")
        self.audio_queue.put(message)
    
    def calc_angle(self, a, b, c):
        if not all([a, b, c]):
            return 180
        if a.visibility < 0.5 or b.visibility < 0.5 or c.visibility < 0.5:
            return 180
        
        pa = np.array([a.x, a.y])
        pb = np.array([b.x, b.y])
        pc = np.array([c.x, c.y])
        
        vba = pa - pb
        vbc = pc - pb
        
        norm_vba = np.linalg.norm(vba)
        norm_vbc = np.linalg.norm(vbc)
        
        if norm_vba == 0 or norm_vbc == 0:
            return 180
        
        cosine = np.dot(vba, vbc) / (norm_vba * norm_vbc)
        cosine = np.clip(cosine, -1.0, 1.0)
        return np.degrees(np.arccos(cosine))
    
    def get_bilateral_angles(self, lm, ex_type):
        angles = {}
        lmk = lambda i: lm[i] if i < len(lm) else None
        
        if ex_type == "squat":
            angles['right'] = self.calc_angle(lmk(24), lmk(26), lmk(28))
            angles['left'] = self.calc_angle(lmk(23), lmk(25), lmk(27))
        elif ex_type == "abduction":
            angles['right'] = self.calc_angle(lmk(24), lmk(12), lmk(14))
            angles['left'] = self.calc_angle(lmk(23), lmk(11), lmk(13))
        elif ex_type == "elbow":
            angles['right'] = self.calc_angle(lmk(12), lmk(14), lmk(16))
            angles['left'] = self.calc_angle(lmk(11), lmk(13), lmk(15))
        elif ex_type == "hipflex":
            angles['right'] = self.calc_angle(lmk(12), lmk(24), lmk(26))
            angles['left'] = self.calc_angle(lmk(11), lmk(23), lmk(25))
        elif ex_type == "wristext":
            angles['right'] = self.calc_angle(lmk(14), lmk(16), lmk(20))
            angles['left'] = self.calc_angle(lmk(13), lmk(15), lmk(19))
        
        return angles
    
    def check_form_correct(self, angle, ex):
        if ex == "squat":
            return angle <= self.down_knee_angle
        elif ex == "abduction":
            return self.abd_up_angle <= angle <= self.abd_max_angle
        elif ex == "elbow":
            return angle <= self.eflex_bent_angle
        elif ex == "hipflex":
            return angle <= self.hflex_bent_angle
        elif ex == "wristext":
            return angle <= self.wext_bent_angle
        return False
    
    def check_perfect_form(self, angle, ex):
        if ex == "squat":
            return angle <= self.squat_perfect_angle
        elif ex == "abduction":
            return angle >= self.abd_perfect_angle
        elif ex == "elbow":
            return angle <= self.eflex_perfect_angle
        elif ex == "hipflex":
            return angle <= self.hflex_perfect_angle
        elif ex == "wristext":
            return angle <= self.wext_perfect_angle
        return False
    
    def calculate_rep_score(self, status_type, perfect_quality_ratio=0):
        if status_type == "SUCCESS":
            if perfect_quality_ratio > 0.8:
                return np.random.randint(95, 101)
            elif perfect_quality_ratio > 0.5:
                return np.random.randint(85, 95)
            else:
                return np.random.randint(75, 85)
        return 0
    
    # Additional methods would follow the same pattern as original soloHelpModes2.py
    # For brevity, core integration methods are shown
    
    def run(self):
        """Main run loop - similar to original but with DB integration"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open video capture device.")
            return
        
        cap.set(3, 1280)
        cap.set(4, 720)
        cap.set(5, self.FPS)
        
        window_name = "SmartPhysio Web Integrated"
        cv2.namedWindow(window_name)
        
        session_start_time = time.time()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.pose.process(rgb_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            
            # Display frame
            cv2.imshow(window_name, frame)
        
        cap.release()
        cv2.destroyAllWindows()
        self.audio_queue.put(None)
        self.audio_thread.join()
        
        # Update final session data
        state = self.exercises[self.current_ex]
        duration = int(time.time() - session_start_time)
        avg_score = np.mean(state['rep_scores']) if state['rep_scores'] else 0
        
        self._update_session(
            total_reps=state['repcount'],
            average_score=avg_score,
            duration_seconds=duration
        )
        
        print(f"\n--- SESSION COMPLETE ---")
        print(f"Total reps: {state['repcount']}")
        print(f"Average Score: {avg_score:.1f}")
        print(f"Duration: {duration}s")
        print(f"View analysis at: http://localhost:5000/analysis?session={self.session_id}")


if __name__ == "__main__":
    mode = ""
    while mode not in ["solo", "assisted"]:
        mode = input("Enter session mode ('solo' or 'assisted'): ").strip().lower()
    
    exercise = input("Enter exercise ('squat', 'abduction', 'elbow', 'hipflex', or 'wristext'): ").strip().lower()
    
    if exercise not in ["squat", "abduction", "elbow", "hipflex", "wristext"]:
        print(f"Invalid exercise '{exercise}'. Defaulting to 'squat'.")
        exercise = "squat"
    
    assistant = SmartPhysioWebIntegrated(exercise, mode)
    assistant.run()
