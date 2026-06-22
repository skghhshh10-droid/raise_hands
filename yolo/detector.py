from ultralytics import YOLO
import cv2
import time
import streamlit as st

# YOLOv11 Pose 모델 로드
@st.cache_resource
def load_model():
    return YOLO("yolo11n-pose.pt")

model = load_model()

# 왼쪽/오른쪽 손들기 판정 함수들
def left_hand_raised(person):
    if len(person) < 11: return False
    nose, ls, le, lw = person[0], person[5], person[7], person[9]
    return lw[1] < le[1] and le[1] < ls[1] and lw[1] < nose[1] and abs(ls[1] - lw[1]) > 40

def right_hand_raised(person):
    if len(person) < 11: return False
    nose, rs, re, rw = person[0], person[6], person[8], person[10]
    return rw[1] < re[1] and re[1] < rs[1] and rw[1] < nose[1] and abs(rs[1] - rw[1]) > 40

# 📢 조장님이 요구한 팀원2 필수 구현 함수
def detect_hand_raise(frame):
    # YOLO 추적 실행
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

            # 너무 작은 객체 제외
            x1, y1, x2, y2 = boxes[i].xyxy[0].cpu().numpy()
            if (x2 - x1) * (y2 - y1) < 10000: continue

            left = left_hand_raised(person)
            right = right_hand_raised(person)
            both = left and right

            status = "NONE"
            if both: status = "BOTH"
            elif left: status = "LEFT"
            elif right: status = "RIGHT"

            # 3초 연속 유지 출석 처리 로직
            if both:
                if track_id not in st.session_state.raise_start:
                    st.session_state.raise_start[track_id] = time.time()

                duration = time.time() - st.session_state.raise_start[track_id]

                if duration >= 3:
                    if track_id not in st.session_state.confirmed_ids:
                        st.session_state.confirmed_ids.add(track_id)
                        st.session_state.attendance[track_id] = True
                        
                        # 팀원3(database) 파일이 완성되면 연동될 저장 로직 호출
                        if 'save_attendance' in globals():
                            save_attendance(track_id)
            else:
                if track_id in st.session_state.raise_start:
                    del st.session_state.raise_start[track_id]

            # 화면 텍스트 출력
            x, y = int(person[0][0]), int(person[0][1])
            cv2.putText(annotated_frame, f"ID:{track_id}", (x, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"{status}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            if track_id in st.session_state.attendance:
                cv2.putText(annotated_frame, "ATTENDED", (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    return annotated_frame

