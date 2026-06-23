from ultralytics import YOLO
import cv2
import streamlit as st


# =========================================================
# 모델 로드
# =========================================================

@st.cache_resource
def load_model():
    return YOLO("yolo11n-pose.pt")


model = load_model()


# =========================================================
# 왼손 들기
# =========================================================

def left_hand_raised(person):

    if len(person) < 11:
        return False

    nose = person[0]

    ls = person[5]
    le = person[7]
    lw = person[9]

    return (
        lw[1] < le[1]
        and le[1] < ls[1]
        and lw[1] < nose[1]
        and abs(ls[1] - lw[1]) > 40
    )


# =========================================================
# 오른손 들기
# =========================================================

def right_hand_raised(person):

    if len(person) < 11:
        return False

    nose = person[0]

    rs = person[6]
    re = person[8]
    rw = person[10]

    return (
        rw[1] < re[1]
        and re[1] < rs[1]
        and rw[1] < nose[1]
        and abs(rs[1] - rw[1]) > 40
    )


# =========================================================
# 손들기 감지
# =========================================================

def detect_hand_raise(frame):

    detected = False

    results = model(
        frame,
        conf=0.70
    )

    annotated_frame = results[0].plot()

    keypoints = results[0].keypoints

    if keypoints is not None:

        xy = keypoints.xy.cpu().numpy()

        for person in xy:

            if len(person) < 11:
                continue

            left = left_hand_raised(person)
            right = right_hand_raised(person)

            if left and right:

                detected = True

                cv2.putText(
                    annotated_frame,
                    "HAND RAISED",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    3
                )

                break

    return detected, annotated_frame
