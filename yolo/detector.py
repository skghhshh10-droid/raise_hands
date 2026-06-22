import streamlit as st
from ultralytics import YOLO
import cv2
import time
import csv
import numpy as np

# ==================================================
# [기존] 왼쪽/오른쪽 손들기 기본 키포인트 판정 함수
# ==================================================
def left_hand_raised(person):
    if len(person) < 11: return False
    nose = person[0]
    ls = person[5]   # 왼어깨
    le = person[7]   # 왼팔꿈치
    lw = person[9]   # 왼손목
    return lw[1] < le[1] and le[1] < ls[1] and lw[1] < nose[1] and abs(ls[1] - lw[1]) > 40

def right_hand_raised(person):
    if len(person) < 11: return False
    nose = person[0]
    rs = person[6]   # 오른어깨
    re = person[8]   # 오른팔꿈치
    rw = person[10]  # 오른손목
    return rw[1] < re[1] and re[1] < rs[1] and rw[1] < nose[1] and abs(rs[1] - rw[1]) > 40

def both_hands_raised(person):
    return left_hand_raised(person) and right_hand_raised(person)


# ==================================================
# 📢 [조장님 요구사항] 팀원2(YOLO) 담당 필수 지정 함수
# 이 함수는 웹캠 프레임 1개를 입력받아 손들기를 감지하고 화면을 그려서 반환합니다.
# ==================================================
def detect_hand_raise(frame):
    # YOLO 추적 실행 (Confidence 70% 이상만 필터링하여 유령 박스 노이즈 제거)
    results = model.track(frame, persist=True, verbose=False, conf=0.70)
    annotated_frame = results[0].plot()

    keypoints = results[0].keypoints
    boxes = results[0].boxes

    if keypoints is not None and boxes is not None and boxes.id is not None:
        xy = keypoints.xy.cpu().numpy()
        ids = boxes.id.cpu().numpy()

        for i, (person, track_id) in enumerate(zip(xy, ids)):
            track_id = int(track_id)
            if len(person) < 11: continue

            # 박스 크기 필터링 (너무 멀리 있는 작은 노이즈 객체 제외)
            x1, y1, x2, y2 = boxes[i].xyxy[0].cpu().numpy()
            if (x2 - x1) * (y2 - y1) < 10000: continue

            # 손들기 상태 판정 (양손 / 왼손 / 오른손)
            left = left_hand_raised(person)
            right = right_hand_raised(person)
            both = left and right

            status = "NONE"
            if both: status = "BOTH"
            elif left: status = "LEFT"
            elif right: status = "RIGHT"

            # ---------------------------------------
            # 3초 연속 유지 출석 처리 로직
            # ---------------------------------------
            if both:  # 기획서 양손 유지 기준 충족 시
                if track_id not in st.session_state.raise_start:
                    st.session_state.raise_start[track_id] = time.time()

                duration = time.time() - st.session_state.raise_start[track_id]

                # 3초 이상 들고 있을 때 출석 확정 및 CSV 저장
                if duration >= 3:
                    if track_id not in st.session_state.confirmed_ids:
                        st.session_state.confirmed_ids.add(track_id)
                        st.session_state.attendance[track_id] = True
                        save_attendance(track_id)
            else:
                # 손을 내리면 타이머 초기화
                if track_id in st.session_state.raise_start:
                    del st.session_state.raise_start[track_id]

            # ---------------------------------------
            # 카메라 화면 위에 텍스트 정보 출력 (ID, 상태, 출석여부)
            # ---------------------------------------
            x, y = int(person[0][0]), int(person[0][1])
            cv2.putText(annotated_frame, f"ID:{track_id}", (x, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"{status}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            if track_id in st.session_state.attendance:
                cv2.putText(annotated_frame, "ATTENDED", (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    return annotated_frame


# ==================================================
# YOLOv11 Pose 모델 로드 (최초 1회 캐싱 로딩)
# ==================================================
@st.cache_resource
def load_model():
    return YOLO("yolo11n-pose.pt")

model = load_model()

# ==================================================
# Streamlit 기본 화면 UI 구성 및 세션 초기화
# ==================================================
st.title("손들기 기반 출석 체크 시스템")
st.write("양손을 3초 이상 들면 출석 처리됩니다.")

if "attendance" not in st.session_state: st.session_state.attendance = {}
if "raise_start" not in st.session_state: st.session_state.raise_start = {}
if "confirmed_ids" not in st.session_state: st.session_state.confirmed_ids = set()

# CSV 출석 결과 저장 함수
def save_attendance(track_id):
    with open("attendance.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([track_id, time.strftime("%Y-%m-%d %H:%M:%S")])

# 웹캠 작동 제어 스위치
run_webcam = st.toggle("웹캠 실행", key="run_webcam")
frame_placeholder = st.empty()

# ==================================================
# 실시간 비디오 스트리밍 루프
# ==================================================
if st.session_state.run_webcam:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("웹캠을 열 수 없습니다.")
    else:
        while cap.isOpened() and st.session_state.run_webcam:
            success, frame = cap.read()
            if not success: break

            # 거울 모드 좌우 반전
            frame = cv2.flip(frame, 1)

            # ✨ 조장님이 요청한 그 함수를 여기서 호출하여 화면을 처리합니다!
            annotated_frame = detect_hand_raise(frame)

            # Streamlit 출력을 위해 RGB 포맷 변환 후 드로우
            annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(annotated_frame, use_container_width=True)
        cap.release()
else:
    st.write("웹캠을 실행해주세요.")

