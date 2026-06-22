import streamlit as st
from ultralytics import YOLO
import cv2
import time
import json  # 기획서 기술 스택에 맞춰 기존 CSV 대신 JSON 저장 방식으로 변경하기 위함
import os
import numpy as np

# ==================================================
# [웹 디자인] 고급스럽고 직관적인 대시보드 스타일 테마 설정
# ==================================================
st.set_page_config(layout="wide", page_title="AI 스마트 강의실", page_icon="🏫")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    html, body, [data-testid="stSidebarCollapse"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    .main-title {
        font-size: 30px; font-weight: 700; color: #1E3A8A; margin-bottom: 5px;
    }
    .status-card {
        background-color: #EFF6FF; border-left: 5px solid #3B82F6;
        padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px;
    }
    .dash-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: white; padding: 25px; border-radius: 12px; text-align: center;
    }
    .badge {
        background-color: #10B981; color: white; padding: 3px 8px;
        border-radius: 4px; font-weight: bold; font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================================================
# [시간 설정] 출석 인정을 위한 연속 손들기 제한 시간 (3초)
# ==================================================
REQUIRED_DURATION = 3.0 

# ==================================================
# [정밀 판정 함수] 단순 오류 동작(머리 긁기, 기지개 등)을 필터링하는 알고리즘
# ==================================================
def is_valid_hand_raise(person, is_left=True):
    """
    YOLO Pose 17개 키포인트를 활용해 한 손이 정상적으로 들렸는지 필터링하는 함수
    """
    if len(person) < 11:
        return False
        
    nose = person[0]
    # 왼쪽/오른쪽 요청에 따른 어깨, 팔꿈치, 손목 인덱스 매핑
    shoulder = person[5] if is_left else person[6]
    elbow = person[7] if is_left else person[8]
    wrist = person[9] if is_left else person[10]
    
    # 키포인트가 제대로 감지되지 않은 좌표(0,0) 예외 처리
    if shoulder[1] == 0 or wrist[1] == 0:
        return False

    # 조건 1: 역전 검사 (기본적으로 손목이 팔꿈치보다 위, 팔꿈치가 어깨보다 위여야 함)
    is_upward = wrist[1] < elbow[1] and elbow[1] < shoulder[1]
    
    # 조건 2 (얼굴 위 검사): 손목이 얼굴(코)의 Y축 위치보다 확실히 위에 도달해 있는가
    is_above_head = wrist[1] < nose[1] - 30 
    
    # 조건 3 (머리 긁기 방지 예외처리): 손이 머리 주변을 만지는 중인지 구별하기 위해 코와의 가로 거리 확보
    is_not_scratching = abs(wrist[0] - nose[0]) > 45
    
    # 조건 4 (만세 기지개 방지 예외처리): 팔이 옆으로 찢어지듯 벌어지면 제외 (가로 거리가 세로 높이보다 크면 탈락)
    height_diff = abs(shoulder[1] - wrist[1])
    width_diff = abs(shoulder[0] - wrist[0])
    is_not_stretching = width_diff < height_diff * 1.3

    return is_upward and is_above_head and is_not_scratching and is_not_stretching

# ==================================================
# [YOLOv11 모델 로드] 캐싱을 적용하여 최초 가중치 한번만 로딩 유도
# ==================================================
@st.cache_resource
def load_model():
    return YOLO("yolo11n-pose.pt")

model = load_model()

# ==================================================
# [세션 상태 초기화] 실시간 웹캠 동적 데이터 소실 방지용 저장소
# ==================================================
if "attendance" not in st.session_state: st.session_state.attendance = {}
if "raise_start" not in st.session_state: st.session_state.raise_start = {}
if "confirmed_ids" not in st.session_state: st.session_state.confirmed_ids = set()

# ==================================================
# [데이터 통합 인터페이스] 팀원 3(출석 데이터 저장)과의 JSON 파일 포맷 싱크 연동 함수
# ==================================================
def save_attendance_json(track_id, timestamp):
    file_path = "attendance.json"
    data = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except json.JSONDecodeError: data = {}
    data[str(track_id)] = timestamp
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==================================================
# [화면 UI 구성] 기획서 와이어프레임 구조에 맞게 화면 좌우 이원화 분할
# ==================================================
st.markdown('<div class="main-title">AI 스마트 강의실 출석체크 🏫</div>', unsafe_allow_html=True)
st.markdown("""
<div class="status-card">
    👋 <b>사용자 안내:</b> 왼손 또는 오른손 중 <b>한 손을 편하게 3초 이상</b> 들고 있으면 출석이 인정됩니다.<br>
    🤖 <i>머리를 만지거나 긁는 행위, 양팔을 옆으로 넓게 벌려 기지개를 켜는 행동은 시스템이 오작동 노이즈로 간주하여 처리하지 않습니다.</i>
</div>
""", unsafe_allow_html=True)

# 좌측 카메라 영상 60%, 우측 대시보드 스탯 정보 40% 분할 비율 적용
col_cam, col_dash = st.columns([1.8, 1.2])

with col_cam:
    st.write("### 📹 강의실 웹캠 모니터링 영역")
    frame_placeholder = st.empty()
    run_webcam = st.toggle("🔌 시스템 탐지 가동 스위치 (On/Off)", key="run_webcam")

with col_dash:
    st.write("### 📊 강의실 출석 현황 통계")
    stat_box = st.empty()
    st.write("---")
    st.write("👥 **실시간 출석 완료 로그 리스트**")
    list_placeholder = st.empty()

# 웹캠 꺼져있을 때 초기 화면 UI 기본값 처리
if not st.session_state.run_webcam:
    frame_placeholder.info("하단의 스위치를 켜면 YOLO 추론 모듈이 시작됩니다.")
    stat_box.markdown(f'<div class="dash-box"><span style="font-size:15px; color:#94A3B8;">현재 확정 출석 인원</span><br><span style="font-size:45px; font-weight:700; color:#10B981;">{len(st.session_state.confirmed_ids)} 명</span></div>', unsafe_allow_html=True)
    list_placeholder.text("대기 중...")

# ==================================================
# [핵심 비디오 추론 루프] 실시간 프레임 캡처 및 YOLO 추적 제어
# ==================================================
if st.session_state.run_webcam:
    cap = cv2.VideoCapture(0)
    # 웹캠 버퍼 해상도 강제 규격화하여 연산 프레임 속도 최적화
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while cap.isOpened() and st.session_state.run_webcam:
        success, frame = cap.read()
        if not success: break

        # 시연자가 거울을 보듯 조작하기 편하게 좌우 반전
        frame = cv2.flip(frame, 1)

        # 중복 노이즈 유령 박스 제거를 위해 confidence 한계치를 0.70으로 지정하여 원천 차단
        results = model.track(frame, persist=True, verbose=False, conf=0.70)
        annotated_frame = results[0].plot()

        keypoints = results[0].keypoints
        boxes = results[0].boxes

        # 화면에 사람이 있고 추적 ID가 확보된 경우에만 판정 진입
        if keypoints is not None and boxes is not None and boxes.id is not None:
            xy = keypoints.xy.cpu().numpy()
            ids = boxes.id.cpu().numpy()

            for i, (person, track_id) in enumerate(zip(xy, ids)):
                track_id = int(track_id)
                if len(person) < 11: continue

                # 멀리 앉은 배경 노이즈 제거용 바운딩박스 면적 최소 컷 오프 적용
                x1, y1, x2, y2 = boxes[i].xyxy[0].cpu().numpy()
                if (x2 - x1) * (y2 - y1) < 12000: continue

                # ==================================================
                # [수정 핵심] 왼손 혹은 오른손 한쪽 단독 손들기 상태 스캔
                # ==================================================
                left = is_valid_hand_raise(person, is_left=True)
                right = is_valid_hand_raise(person, is_left=False)
                
                status = "NONE"
                if left and right: status = "BOTH"
                elif left: status = "LEFT"
                elif right: status = "RIGHT"

                # 화면 텍스트 오버레이용 좌표 따기 (얼굴 코 좌표 기준)
                x, y = int(person[0][0]), int(person[0][1])
                
                # ==================================================
                # [수정 핵심] 한 손이라도 탐지되면 타이머 누적 시작
                # ==================================================
                if left or right:
                    if track_id not in st.session_state.raise_start:
                        st.session_state.raise_start[track_id] = time.time()

                    # 실시간 손들기 경과 시간 계산
                    duration = time.time() - st.session_state.raise_start[track_id]
                    
                    # 💡 질문 해결: 출석이 차오르는 시각적 경로 텍스트 표현 피드백 코드
                    cv2.putText(annotated_frame, f"STATUS: {status} ({duration:.1f}s / {REQUIRED_DURATION}s)", 
                                (x - 50, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2)

                    # 설정된 목표 시간(3초) 충족 시 출석 완료 확정
                    if duration >= REQUIRED_DURATION:
                        if track_id not in st.session_state.confirmed_ids:
                            st.session_state.confirmed_ids.add(track_id)
                            log_time = time.strftime("%H:%M:%S")
                            st.session_state.attendance[f"ID {track_id}"] = log_time
                            
                            # 팀원 3 연동용 JSON 자동 백업 파일 세이브 함수 트리거
                            save_attendance_json(track_id, log_time)
                else:
                    # 손을 내리면 즉시 카운트 초기화하여 엄격한 시간 필터링 적용
                    if track_id in st.session_state.raise_start:
                        del st.session_state.raise_start[track_id]
                    
                    cv2.putText(annotated_frame, "STATUS: NONE", (x - 50, y - 35), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)

                # 이미 성공 처리가 끝난 ID 대상자는 상시 완장 마크 오버레이 표시
                if track_id in st.session_state.confirmed_ids:
                    cv2.putText(annotated_frame, "★ ATTENDED ★", (x - 50, y - 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 렌더링을 위해 BGR 포맷 이미지를 RGB로 변환하여 캔버스 드로우
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(annotated_frame, use_container_width=True)

        # 우측 패널 대시보드 웹 스탯 컴포넌트 실시간 동기화 업데이트
        stat_box.markdown(f'<div class="dash-box"><span style="font-size:15px; color:#94A3B8;">현재 확정 출석 인원</span><br><span style="font-size:45px; font-weight:700; color:#10B981;">{len(st.session_state.confirmed_ids)} 명</span></div>', unsafe_allow_html=True)
        
        # 가독성 높은 실시간 출석 통계 뱃지 출력 스크립트
        if st.session_state.attendance:
            log_html = ""
            for student_id, att_time in st.session_state.attendance.items():
                log_html += f"<p style='margin-bottom:8px;'>🟢 <b>{student_id}</b> 학생 — <span class='badge'>{att_time} 출석완료</span></p>"
            list_placeholder.markdown(log_html, unsafe_allow_html=True)
        else:
            list_placeholder.markdown("<p style='color:#9CA3AF;'>출석 인정 기록이 비어있습니다.</p>", unsafe_allow_html=True)

    cap.release()
