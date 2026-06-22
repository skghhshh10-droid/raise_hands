# =========================================================
# AI Smart Classroom
# 최종 통합 버전
# =========================================================

import streamlit as st
import pandas as pd

from database.attendance import (
    save_attendance,
    get_attendance
)

from dashboard.statistics import (
    attendance_count,
    attendance_rate
)

# 나중에 YOLO 연결
from yolo.detector import detect_hand_raise


# =========================================================
# Streamlit 설정
# =========================================================

st.set_page_config(
    page_title="AI Smart Classroom",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass


# =========================================================
# DB 데이터 로드
# =========================================================

try:

    attendance_data = get_attendance()

    if attendance_data:
        students = pd.DataFrame(attendance_data)
    else:
        students = pd.DataFrame()

except Exception as e:

    students = pd.DataFrame()


# =========================================================
# 통계
# =========================================================

count = attendance_count()

TOTAL_STUDENTS = 30

rate = attendance_rate(TOTAL_STUDENTS)


# =========================================================
# 헤더
# =========================================================

st.markdown("""
<div class="top-header">
<div>
<h1>👋 AI Smart Classroom</h1>
<p>손들기 인식을 통한 스마트 출석 시스템</p>
</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 사이드바
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="logo">
        ✋ 손들기<br>
        출석 시스템
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "",
        [
            "📊 대시보드",
            "⏱ 실시간 출석",
            "👨‍🎓 학생 관리",
            "📈 참여도 분석"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button(
        "📷 웹캠 시작",
        use_container_width=True
    ):
        st.success("웹캠 시작")

    if st.button(
        "⛔ 웹캠 종료",
        use_container_width=True
    ):
        st.warning("웹캠 종료")



# =========================================================
# 대시보드
# =========================================================

if page == "📊 대시보드":

    st.markdown(
        '<div class="card-title">실시간 카메라</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1.5, 1])

    # -------------------------------------------------
    # 카메라 영역
    # -------------------------------------------------

    with left:

        st.markdown("""
        <div class="camera-box">
        <div class="camera-placeholder">
        YOLO 결과 영상 표시 영역
        </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------
    # 통계 카드
    # -------------------------------------------------

    with right:

        c1, c2, c3 = st.columns(3)

        metrics = [
            ("출석 인원", f"{count}명"),
            ("출석률", f"{rate}%"),
            ("시스템", "정상")
        ]

        for col, metric in zip(
            [c1, c2, c3],
            metrics
        ):

            with col:

                st.metric(
                    metric[0],
                    metric[1]
                )

    st.divider()

    # -------------------------------------------------
    # 출석 현황
    # -------------------------------------------------

    st.subheader("📋 출석 현황")

    if len(students) > 0:

        st.dataframe(
            students,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "출석 데이터가 없습니다."
        )


# =========================================================
# 실시간 출석
# =========================================================

elif page == "⏱ 실시간 출석":

    st.title("실시간 출석")

    st.info(
        "YOLO 손들기 인식 화면"
    )

    st.markdown(
        "정담원님 YOLO 코드 연동 예정"
    )


# =========================================================
# 학생 관리
# =========================================================

elif page == "👨‍🎓 학생 관리":

    st.title("학생 관리")

    if len(students) > 0:

        st.dataframe(
            students,
            use_container_width=True
        )

    else:

        st.info(
            "등록된 학생이 없습니다."
        )


# =========================================================
# 참여도 분석
# =========================================================

elif page == "📈 참여도 분석":

    st.title("참여도 분석")

    st.metric(
        "현재 출석률",
        f"{rate}%"
    )
