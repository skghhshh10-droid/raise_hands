# app.py


# =========================================================
# AI Smart Classroom
# =========================================================

import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
from yolo.detector import detect_hand_raise
import cv2
from database.attendance import (
    get_students,
    register_student,
    save_attendance,
    get_attendance,
    delete_student,
    delete_attendance
)



from dashboard.statistics import (
    attendance_count,
    attendance_rate
)




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
# 데이터
# =========================================================

attendance_df = pd.DataFrame(
    get_attendance()
)

students_df = pd.DataFrame(
    get_students()
)

count = attendance_count()

TOTAL_STUDENTS = max(
    len(students_df),
    1
)

rate = attendance_rate(
    TOTAL_STUDENTS
)


# =========================================================
# 헤더
# =========================================================


st.markdown(f"""
<div style="
text-align:center;
padding:30px;
background:linear-gradient(
180deg,
#eef6ff,
#f8fafc
);
border-radius:24px;
margin-bottom:20px;
">

<h1 style="
margin-bottom:10px;
font-size:42px;
font-weight:800;
color:#111827;
">
🎓 AI SMART CLASSROOM
</h1>

<p style="
font-size:18px;
color:#64748b;
margin-bottom:20px;
">
실시간 YOLO Pose 기반 스마트 출석 및 참여도 관리 시스템
</p>

<div style="
display:flex;
justify-content:center;
gap:12px;
flex-wrap:wrap;
margin-bottom:25px;
">

<span style="
padding:8px 16px;
background:white;
border:1px solid #e5e7eb;
border-radius:999px;
font-size:14px;
font-weight:600;
">
✅ 실시간 손들기 인식
</span>

<span style="
padding:8px 16px;
background:white;
border:1px solid #e5e7eb;
border-radius:999px;
font-size:14px;
font-weight:600;
">
✅ 자동 출석 체크
</span>

<span style="
padding:8px 16px;
background:white;
border:1px solid #e5e7eb;
border-radius:999px;
font-size:14px;
font-weight:600;
">
✅ 참여도 분석
</span>

</div>

<div style="
display:flex;
justify-content:center;
gap:16px;
flex-wrap:wrap;
">

<div style="
background:white;
padding:15px;
border-radius:18px;
min-width:130px;
box-shadow:0 4px 15px rgba(0,0,0,.05);
">
<div style="font-size:32px;font-weight:800;">
{len(students_df)}
</div>
<div>등록 학생</div>
</div>

<div style="
background:white;
padding:15px;
border-radius:18px;
min-width:130px;
box-shadow:0 4px 15px rgba(0,0,0,.05);
">
<div style="font-size:32px;font-weight:800;">
{count}
</div>
<div>출석 학생</div>
</div>

<div style="
background:white;
padding:15px;
border-radius:18px;
min-width:130px;
box-shadow:0 4px 15px rgba(0,0,0,.05);
">
<div style="font-size:32px;font-weight:800;">
{rate}%
</div>
<div>출석률</div>
</div>

</div>

</div>
""", unsafe_allow_html=True)

# =========================================================
# 관리자 인증
# =========================================================

ADMIN_ID = "admin"
ADMIN_PW = "1234"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


# =========================================================
# 사이드바
# =========================================================

with st.sidebar:

    st.markdown("""
    <div style="
    text-align:center;
    padding:20px;
    margin-bottom:20px;
    background:linear-gradient(135deg,#6366f1,#8b5cf6);
    border-radius:20px;
    color:white;
    ">
    <h3>🎓 AI Smart Classroom</h3>
    <p>관리자 시스템</p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------
    # 관리자 로그인
    # ------------------------

    if not st.session_state.is_admin:

        st.subheader("🔐 관리자 로그인")

        admin_id = st.text_input(
            "아이디"
        )

        admin_pw = st.text_input(
            "비밀번호",
            type="password"
        )

        if st.button(
            "로그인",
            width="stretch"
        ):

            if (
                admin_id == ADMIN_ID
                and admin_pw == ADMIN_PW
            ):

                st.session_state.is_admin = True

                st.success(
                    "관리자 로그인 성공"
                )

                st.rerun()

            else:

                st.error(
                    "아이디 또는 비밀번호 오류"
                )

    else:

        st.success(
            "🔒 관리자 로그인 상태"
        )

        st.caption(
            "관리자 전용 기능 사용 가능"
        )

        if st.button(
            "로그아웃",
            width="stretch"
        ):

            st.session_state.is_admin = False

            st.rerun()

    st.divider()

    # ------------------------
    # 메뉴
    # ------------------------

    if st.session_state.is_admin:

        menu = [
            "📊 대시보드",
            "📝 출석 체크",
            "👨‍🎓 학생 관리",
            "➕ 학생 등록",
            "📈 참여도 분석"
        ]

    else:

        menu = [
            "📊 대시보드",
            "📝 출석 체크",
            "📈 참여도 분석"
        ]

    page = st.radio(
        "메뉴",
        menu,
        label_visibility="collapsed"
    )




# =========================================================
# 대시보드
# =========================================================

if page == "📊 대시보드":

    # KPI 카드
    k1, k2, k3 = st.columns(3)

    k1.metric("👨‍🎓 등록 학생", len(students_df))
    k2.metric("🙋 출석 학생", count)
    k3.metric("📈 출석률", f"{rate}%")

    st.divider()

    # =========================
    # 출석률 분석 + 출석 요약
    # =========================

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("📈 출석률 분석")

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=rate,
                title={"text": "출석률"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#6366f1"}
                }
            )
        )

        gauge.update_layout(
            height=280,
            margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
            )
        )

        st.markdown(
            f"""
            <h2 style='
            text-align:center;
            color:#4f46e5;
            font-weight:800'>
            현재 출석률 {rate}%
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.plotly_chart(
            gauge,
            width="stretch"
        )

    with c2:

        st.subheader("📋 출석 요약")

        st.metric("등록 학생", len(students_df))
        st.metric("출석 학생", count)
        st.metric("출석률", f"{rate}%")

        st.progress(rate / 100)

        st.caption(
            f"전체 {TOTAL_STUDENTS}명 중 "
            f"{count}명 출석"
        )

    st.divider()

    # =========================
    # 최근 출석
    # =========================

    st.subheader("🕒 최근 출석")

    if len(attendance_df) > 0:

        st.dataframe(
            attendance_df.tail(5),
            use_container_width=True,
            hide_index=True,
            height=220
        )

        with st.expander("📋 전체 출석 현황 보기"):

            st.dataframe(
                attendance_df,
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info("출석 데이터가 없습니다.")

# =========================================================
# 출석 체크
# =========================================================

elif page == "📝 출석 체크":

    st.title("📝 출석 체크")

    students = get_students()

    if len(students) == 0:

        st.warning(
            "먼저 학생을 등록하세요."
        )

    else:

        student_name = st.selectbox(
            "👤 학생 선택",
            [s["name"] for s in students]
        )

        st.info(
            """
            📷 카메라로 사진을 촬영하면
            YOLO Pose가 손들기 여부를 분석합니다.
            """
        )

        camera_image = st.camera_input(
            "📷 사진 촬영"
        )

        if camera_image is not None:

            file_bytes = np.asarray(
                bytearray(camera_image.read()),
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                file_bytes,
                cv2.IMREAD_COLOR
            )

            detected, result_frame = detect_hand_raise(
                frame
            )

            st.image(
                result_frame,
                channels="BGR",
                width="stretch"
            )

            if detected:
                st.write("선택 학생:", student_name)
                success = save_attendance(
                    student_name
                )

                if success:

                    st.success(
                        f"✅ {student_name} 출석 완료"
                    )

                    st.balloons()

                    st.rerun()

                else:

                    st.warning(
                        "이미 출석한 학생입니다."
                    )

            else:

                st.error(
                    "🙅 손들기 자세가 감지되지 않았습니다."
                )

        st.divider()

        st.subheader("📋 오늘 출석 현황")

        if len(attendance_df) > 0:

            st.dataframe(
                attendance_df,
                width="stretch",
                hide_index=True
            )

            # =====================
            # 관리자 전용 출석 삭제
            # =====================

            if st.session_state.is_admin:

                st.divider()

                st.subheader(
                    "🔒 관리자 전용 - 출석 기록 삭제"
                )

                delete_att = st.selectbox(
                    "삭제할 출석 기록",
                    attendance_df["student_id"]
                    .astype(str)
                    .tolist()
                )

                st.warning(
                    "삭제된 출석 기록은 복구할 수 없습니다."
                )

                if st.button(
                    "🗑 출석 삭제",
                    width="stretch"
                ):

                    success = delete_attendance(
                        delete_att
                    )

                    if success:

                        st.success(
                            "출석 기록 삭제 완료"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "출석 삭제 실패"
                        )

        else:

            st.info(
                "아직 출석 데이터가 없습니다."
            )



# =========================================================
# 학생 관리
# =========================================================

elif page == "👨‍🎓 학생 관리":

    if not st.session_state.is_admin:

        st.error(
            "🔒 관리자만 접근 가능합니다."
        )

        st.stop()

    st.title("👨‍🎓 학생 관리")

    search = st.text_input(
        "🔍 학생 검색"
    )

    view_df = students_df.copy()

    if (
        search
        and len(students_df) > 0
        and "name" in students_df.columns
    ):

        view_df = students_df[
            students_df["name"]
            .astype(str)
            .str.contains(
                search,
                case=False
            )
        ]

    if len(view_df) > 0:

        st.dataframe(
            view_df,
            width="stretch",
            hide_index=True
        )

        st.caption(
            f"총 {len(view_df)}명 조회"
        )

    else:

        st.info(
            "검색 결과가 없습니다."
        )

    st.divider()

    st.subheader("🗑 학생 삭제")

    students = get_students()

    if len(students) > 0:

        delete_target = st.selectbox(
            "삭제할 학생 선택",
            [
                f"{s['student_id']} - {s['name']}"
                for s in students
            ]
        )

        st.warning(
            "삭제된 학생은 복구할 수 없습니다."
        )

        if st.button(
            "🗑 학생 삭제",
            width="stretch"
        ):

            student_id = delete_target.split(" - ")[0]

            success = delete_student(
                student_id
            )

            if success:

                st.success(
                    "학생 삭제 완료"
                )

                st.rerun()

            else:

                st.error(
                    "학생 삭제 실패"
                )





# =========================================================
# 학생 등록
# =========================================================

elif page == "➕ 학생 등록":

    if not st.session_state.is_admin:

        st.error(
            "🔒 관리자만 접근 가능합니다."
        )

        st.stop()

    st.title("➕ 학생 등록")

    st.info(
        "학생을 등록하면 출석 체크 메뉴에서 "
        "손들기 인식을 통해 출석 처리가 가능합니다."
    )

    col1, col2 = st.columns(2)

    with col1:

        student_id = st.text_input(
            "🎫 학번"
        )

    with col2:

        name = st.text_input(
            "👤 이름"
        )

    st.divider()
    
    if st.button(
        "✅ 학생 등록",
        width="stretch"
    ):
    
        if not student_id or not name:
    
            st.warning(
                "학번과 이름을 입력하세요."
            )
    
        else:
    
            success = register_student(
                student_id,
                name
            )
    
            if success:
    
                st.success(
                    f"✅ {name} 학생 등록 완료"
                )

                st.balloons()
    
                st.rerun()
    
            else:
    
                st.error(
                    "이미 등록된 학번입니다."
                )
    
    st.divider()

    st.subheader("📋 등록 학생 현황")
    
    if len(students_df) > 0:
    
        st.dataframe(
            students_df,
            width="stretch",
            hide_index=True
        )
    
        st.caption(
            f"총 {len(students_df)}명 등록"
        )
    
    else:
    
        st.info(
            "아직 등록된 학생이 없습니다."
        )



# =========================================================
# 참여도 분석
# =========================================================

elif page == "📈 참여도 분석":

    st.title("📈 참여도 분석")

    if len(students_df) > 0 and "name" in students_df.columns:

        chart_data = pd.DataFrame({
            "학생": students_df["name"],
            "참여도": [80] * len(students_df)
        })

        st.subheader("🏆 학생 참여도")

        fig = px.bar(
            chart_data,
            x="학생",
            y="참여도",
            title="학생 참여도 순위"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "등록된 학생 데이터가 없습니다."
        )

    st.divider()

    st.metric(
        "현재 출석률",
        f"{rate}%"
    )

    st.progress(
        min(rate / 100, 1.0)
    )

