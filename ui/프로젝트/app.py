# =========================================================
# 실시간 출석 대시보드 (app.py)
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================================================
# Streamlit 페이지 설정
# =========================================================
st.set_page_config(page_title="실시간 출석 대시보드", layout="wide")

# =========================================================
# CSS 파일 불러오기
# =========================================================
with open("style.css", encoding="utf-8") as f:
     # CSS 내용을 읽어 <style> 태그 안에 삽입
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================================================
# 예제 학생 데이터 생성
# =========================================================
students = pd.DataFrame({
    "ID":[1,2,3,4,5],
    "이름":["김철수","이영희","박민수","최지우","정하늘"],
    "출석 상태":["출석 완료","출석 완료","출석 완료","손들기 감지","미출석"],
    "손들기 시간":["10:30:12","10:30:18","10:30:25","-","-"],
    "참여도 점수":[95,85,80,70,40]
})

# =========================================================
# 상단 헤더 출력
# =========================================================
st.markdown("""
<div class="top-header">
<div>
<h1>👋 실시간 출석 대시보드</h1>
<p>손들기 인식을 통한 스마트 출석 체크 시스템</p>
</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 사이드바
# =========================================================
with st.sidebar:

    st.markdown(
        '<div class="logo">✋ 손들기<br>출석 시스템</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "",
        [
            "📊 대시보드",
            "⏱ 실시간 출석",
            "👨‍🎓 학생 관리",
            "📝 퀴즈 모드",
            "📈 참여도 분석"
        ],
        label_visibility="collapsed"
    )
    st.divider()
    st.button("📷 웹캠 시작", use_container_width=True)
    st.button("⛔ 웹캠 종료", use_container_width=True)
    st.button("🔄 출석 초기화", use_container_width=True)
    st.download_button("📥 CSV 다운로드", students.to_csv(index=False), "attendance.csv")

# =========================================================
# 대시보드 페이지
# =========================================================
if page == "📊 대시보드":

    st.markdown(
        '<div class="card-title">실시간 카메라</div>',
        unsafe_allow_html=True
    )

    left,right = st.columns([1.55,1])

    # -----------------------------------------------------
    # 왼쪽 : 카메라 영역
    # -----------------------------------------------------
    with left:
        st.markdown("""
        <div class="camera-box">
        <div class="camera-placeholder">
        YOLO Pose 결과 영상 표시 영역
        </div>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # 오른쪽 : 통계 카드
    # -----------------------------------------------------
    with right:
        c1,c2,c3,c4 = st.columns(4)
        metrics=[("현재 인원","5명"),("출석 인원","3명"),("출석률","60%"),("퀴즈 모드","진행 중")]
        for col,m in zip([c1,c2,c3,c4],metrics):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                <div class='metric-label'>{m[0]}</div>
                <div class='metric-value'>{m[1]}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
        <div class="quiz-card">
        <h3>🏆 퀴즈 진행 현황</h3>
        <p>현재 문제 3/5 · 참여 학생 4명 · 정답률 80%</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1,col2 = st.columns([1.1,1])

    # -----------------------------------------------------
    # 출석 현황 테이블
    # -----------------------------------------------------
    with col1:
        st.markdown('<div class="section-title">📋 출석 현황</div>', unsafe_allow_html=True)
        st.dataframe(students, use_container_width=True, hide_index=True)

    # -----------------------------------------------------
    # 참여도 랭킹
    # -----------------------------------------------------
    with col2:

        card = st.container(border=True)

        with card:

            st.markdown(
                '<div class="section-title">🏆 참여도 랭킹</div>',
                unsafe_allow_html=True
            )

            ranking = [
                ("🥇","김철수",95),
                ("🥈","이영희",85),
                ("🥉","박민수",80),
                ("4","최지우",70),
                ("5","정하늘",40)
            ]

            for rank, name, score in ranking:

                c1, c2, c3 = st.columns([1,6,1])

                with c1:
                    st.write(rank)

                with c2:
                    st.progress(score/100)

                with c3:
                    st.write(f"{score}점")

# =========================================================
# 실시간 출석 페이지
# =========================================================
elif page == "⏱ 실시간 출석":

    st.title("실시간 출석")

    st.info("YOLO 출석 화면")

# =========================================================
# 학생 관리 페이지
# =========================================================
elif page == "👨‍🎓 학생 관리":

    st.title("학생 관리")

    st.dataframe(students)

# =========================================================
# 퀴즈 모드 페이지
# =========================================================
elif page == "📝 퀴즈 모드":

    st.title("퀴즈 모드")

# =========================================================
# 참여도 분석 페이지
# =========================================================
elif page == "📈 참여도 분석":

    st.title("참여도 분석")