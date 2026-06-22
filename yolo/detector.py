# YOLO 손들기 감지 모듈

import streamlit as st
from ultralytics import YOLO
import cv2
import time
import json
import os
import numpy as np

# 페이지 기본 설정 (가장 상단에 위치)
st.set_page_config(layout="wide", page_title="AI 스마트 강의실", page_icon="🏫")

# ==================================================
# 😎 세련된 디자인을 위한 Custom CSS 주입
# ==================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
    html, body, [data-testid="stSidebarCollapse"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    .main-title {
        font-size: 32px; font-weight: 700; color: #1E3A8A; margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px; color: #6B7280; margin-bottom: 20px;
    }
    .status-card {
        background-color: #F3F4F6; border-left: 5px solid #3B82F6;
        padding: 15px; border-radius: 8px; margin-bottom: 20px;
    }
    .dash-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;
    }
    .attendance-badge {
        background-color: #10B981; color: white; padding: 4px 8px;
        border-radius: 4px; font-weight: bold; font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================================================
# ⚙️ 시스템 설정 변수 (시간 기준 변경 가능)
# ==================================================
REQUIRED_DURATION = 3.0  # 출석 인정 시간 기준 (3초)

# ==================================================
# [팀원 2 핵심] 정밀 손들기 판정 및 예외처리 함수
# ==================================================
def is_valid_hand_raise(person, is_left=True):
    """
    단순 오류 동작(머리 긁기, 기지개)을 걸러내는 정밀 손들기 판정
    """
    if len(person) < 11:
        return False
        
    nose = person[0]
    # 키포인트 인덱스 설정 (왼쪽/오른쪽 분기)
    shoulder = person[5] if is_left else person[6]
    elbow = person[7] if is_left else person[8]
    wrist = person[9] if is_left else person[10]
    
    # 0점 좌표(감지 실패) 예외 처리
    if shoulder[1] == 0 or wrist[1] == 0:
        return False

    # 기본 조건: 손목 < 팔꿈치 < 어깨 (OpenCV 좌표계 상 위로 갈수록 Y값이 작음)
    is_upward = wrist[1] < elbow[1] and elbow[1] < shoulder[1]
    
    # 예외 필터 1: 코(머리)보다 손목이 확실히 위에 있는가?
    is_above_head = wrist[1] < nose[1] - 30 
    
    # 예외 필터 2 (머리 긁기 방지): 손목이 얼굴 중심(X축)에 지나치게 붙어있는가?
    is_not_scratching = abs(wrist[0] - nose[0]) > 40
    
    # 예외 필터 3 (기지개 방지): 팔이 옆으로 너무 벌어졌는가? (X축 거리가 Y축 높이차보다 크면 기지개)
    height_diff = abs(shoulder[1] - wrist[1])
    width_diff = abs(shoulder[0] - wrist[0])
    is_not_stretching = width_diff < height_diff * 1.3

    return is_upward and is_above_head and is_not_scratching and is_not_stretching

# ==================================================
# YOLOv11 또는 v8 모델 로드
# ==================================================
@st.cache_resource
def load_model():
    return YOLO("yolo11n-pose.pt")  # 제공해주신 기존의 코드를 따라 yolo11n-pose로 로드합니다.

model = load_model()

# 세션 상태 초기화
if "attendance" not in st.session_state: st.session_state.attendance = {}
if "raise_start" not in st.session_state: st.session_state.raise_start = {}
if "confirmed_ids" not in st.session_state: st.session_state.confirmed_ids = set()

# ==================================================
# 웹 UI 레이아웃 구성
# ==================================================
st.markdown('<div class="main-title">AI 스마트 강의실 🏫</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">YOLO Pose 기반 정밀 손들기 출석 시스템 (MVP)</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-card">
    📌 <b>출석 방법:</b> 카메라를 정면으로 바라보고 <b>왼손 또는 오른손 중 한 손을 번쩍 {REQUIRED_DURATION}초 이상</b> 들고 계시면 출석 패널에 등록됩니다.<br>
    ⚠️ <i>주의: 머리를 긁거나 양옆으로 기지개를 켜는 동작은 출석으로 인정되지 않습니다.</i>
</div>
""", unsafe_allow_html=True)

col_cam, col_dash = st.columns([1.8, 1.2])

with col_cam:
    st.write("### 📹 캠 스태프 모니터링")
    frame_placeholder = st.empty()
    run_webcam = st.toggle("🔌 시스템 가동 (웹캠 On/Off)", key="run_webcam")

with col_dash:
    st.write("### 📊 실시간 대시보드 정보")
    stat_box = st.empty()
    st.write("---")
    st.write("👥 **출석 인정 로그**")
    list_placeholder = st.empty()

if not st.session_state.run_webcam:
    frame_placeholder.info("시스템 가동 스위치를 켜주세요.")
    stat_box.markdown(f'<div class="dash-box"><span style="font-size:16px;">현재 출석 인원</span><br><span style="font-size:48px; font-weight:700; color:#10B981;">{len(st.session_state.confirmed_ids)}명</span></div>', unsafe_allow_html=True)
    list_placeholder.text("카메라가 비활성화 상태입니다.")

# ==================================================
# 핵심 비디오 루프
# ==================================================
if st.session_state.run_webcam:
    cap = cv2.VideoCapture(0)
    
    # 해상도 조절로 연산 속도 및 트래킹 안정성 향상
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while cap.isOpened() and st.session_state.run_webcam:
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1)

        # 중요: 추론 단계에서 conf=0.70을 주어 흐릿한 노이즈 박스(캡처 속 중복 생성 박스)들이 아예 안 만들어지게 통제!
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
                if (x2 - x1) * (y2 - y1) < 12000: continue

                # [수정 핵심] 왼손 혹은 오른손 중 하나라도 들려있는지 검사
                left = is_valid_hand_raise(person, is_left=True)
                right = is_valid_hand_raise(person, is_left=False)
                
                # 현재 상태 텍스트 정의
                status = "NONE"
                if left and right:
                    status = "BOTH"
                elif left:
                    status = "LEFT"
                elif right:
                    status = "RIGHT"

                x, y = int(person[0][0]), int(person[0][1])
                
                # 한 손이라도 들려있다면 타이머 작동 시작
                if left or right:
                    if track_id not in st.session_state.raise_start:
                        st.session_state.raise_start[track_id] = time.time()

                    duration = time.time() - st.session_state.raise_start[track_id]
                    
                    # 💡 시각화 강화: 눈에 보이는 경로를 만들기 위해 실시간 시간 흐름을 화면에 텍스트 출력
                    cv2.putText(annotated_frame, f"STATUS: {status} ({duration:.1f}s / {REQUIRED_DURATION}s)", 
                                (x - 40, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

                    # 설정된 기준 시간(3.0초) 이상 유지 완료 시 출석 인정
                    if duration >= REQUIRED_DURATION:
                        if track_id not in st.session_state.confirmed_ids:
                            st.session_state.confirmed_ids.add(track_id)
                            st.session_state.attendance[f"ID {track_id}"] = time.strftime("%H:%M:%S")
                else:
                    # 손을 내리면 누적 타이머 삭제
                    if track_id in st.session_state.raise_start:
                        del st.session_state.raise_start[track_id]
                    
                    # 아무 손도 안 들고 있을 때는 일반 NONE 상태 표시
                    cv2.putText(annotated_frame, f"STATUS: NONE", 
                                (x - 40, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                # 최종 출석 완료된 대상자 표시
                if track_id in st.session_state.confirmed_ids:
                    cv2.putText(annotated_frame, "★ PASSED ★", (x - 40, y - 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 디자인 정돈하여 Streamlit 웹에 전송
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(annotated_frame, use_container_width=True)

        # 우측 대시보드 UI 실시간 렌더링
        stat_box.markdown(f'<div class="dash-box"><span style="font-size:16px; color:#94A3B8;">현재 출석 인원</span><br><span style="font-size:48px; font-weight:700; color:#10B981;">{len(st.session_state.confirmed_ids)}명</span></div>', unsafe_allow_html=True)
        
        # 목록 디자인 가공하여 출력
        if st.session_state.attendance:
            log_html = ""
            for k, v in st.session_state.attendance.items():
                log_html += f"<p style='margin-bottom:8px;'>🟢 <b>{k}</b> 번 학생 — <span class='attendance-badge'>{v} 출석완료</span></p>"
            list_placeholder.markdown(log_html, unsafe_allow_html=True)
        else:
            list_placeholder.markdown("<p style='color:#9CA3AF;'>출석 대기 중인 학생이 없습니다.</p>", unsafe_allow_html=True)

    cap.release()

