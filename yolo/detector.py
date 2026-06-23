from ultralytics import YOLO
import cv2
import streamlit as st


# =========================================================
# YOLO Pose 모델 로드
# =========================================================

@st.cache_resource
def load_model():
    return YOLO("yolo11n-pose.pt")


model = load_model()


# =========================================================
# 왼손 들기
# =========================================================

def left_hand_raised(person):

    try:

        left_shoulder = person[5]
        left_wrist = person[9]

        return left_wrist[1] < left_shoulder[1]

    except:
        return False


# =========================================================
# 오른손 들기
# =========================================================

def right_hand_raised(person):

    try:

        right_shoulder = person[6]
        right_wrist = person[10]

        return right_wrist[1] < right_shoulder[1]

    except:
        return False


# =========================================================
# 손들기 감지
# =========================================================

def detect_hand_raise(frame):

    detected = False

    results = model(
        frame,
        conf=0.4
    )

    annotated_frame = results[0].plot()

    keypoints = results[0].keypoints

    if keypoints is not None:

        persons = keypoints.xy.cpu().numpy()

        for person in persons:

            if len(person) < 11:
                continue

            left = left_hand_raised(person)
            right = right_hand_raised(person)

            # 발표용: 한 손만 들어도 인정
            if left or right:

                detected = True

                cv2.putText(
                    annotated_frame,
                    "HAND RAISED",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    3
                )

                cv2.putText(
                    annotated_frame,
                    f"LEFT:{left} RIGHT:{right}",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                break

        if not detected:

            cv2.putText(
                annotated_frame,
                "NO HAND RAISED",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )

    return detected, annotated_frame
