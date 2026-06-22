# =========================================================
# 실시간 출석 대시보드 (app.py)
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container

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
# 카드 스타일 생성
# =========================================================
CARD_STYLE = """
    {
        background: white;
        border-radius: 24px;
        padding: 24px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 24px rgba(0,0,0,.06);
        margin-bottom: 20px;
    }
    """

DASHBOARD_CARD = """
{
    background: white;
    border-radius: 24px;
    padding: 24px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 24px rgba(0,0,0,.06);
    min-height: 320px;
}
"""

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
            "🎥 수업 진행",
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
# 상단 헤더 출력
# =========================================================
page_titles = {
    "📊 대시보드": "대시보드",
    "🎥 수업 진행": "수업 진행",
    "⏱ 실시간 출석": "실시간 출석",
    "👨‍🎓 학생 관리": "학생 관리",
    "📝 퀴즈 모드": "퀴즈 모드",
    "📈 참여도 분석": "참여도 분석"
}

st.markdown(
    f"""
    <div class="top-header">
        <div>
            <h1>👋 {page_titles[page]}</h1>
            <p>손들기 인식을 통한 스마트 출석 체크 시스템</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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
        실시간 카메라 영역
        </div>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # 오른쪽 : 통계 카드
    # -----------------------------------------------------
    with right:
        c1,c2,c3,c4 = st.columns(4)
        metrics=[("현재 인원","5명"),("출석 인원","3명"),("출석률","60%"),("퀴즈 모드","진행 중")]
        for col,m in zip([c1,c2,c3],metrics):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                <div class='metric-label'>{m[0]}</div>
                <div class='metric-value'>{m[1]}</div>
                </div>
                """, unsafe_allow_html=True)
        with c4:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>퀴즈 모드</div>
                <div class='metric-status'>진행 중</div>
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

        with stylable_container(
            key="attendance_card",
            css_styles=DASHBOARD_CARD
        ):

            st.markdown(
                '<div class="section-title">📋 출석 현황</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                students,
                use_container_width=True,
                hide_index=True
            )

    # -----------------------------------------------------
    # 참여도 랭킹
    # -----------------------------------------------------
    with col2:

        with stylable_container(
            key="ranking_card",
            css_styles=DASHBOARD_CARD
        ):

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
# 수업 진행 페이지
# =========================================================

elif page == "🎥 수업 진행":

    top_left, top_right = st.columns([2.2, 1])

    # 카메라
    with top_left:

        st.html("""
        <div class="live-camera-card">

            <div class="camera-title">
                실시간 카메라 화면
            </div>

            <div class="camera-preview">
                ✋
            </div>

            <div class="rec-text">
                🔴 REC
            </div>

        </div>
        """)

    # 상태 카드
    with top_right:

        st.markdown("""
        <div class="status-card">
            <div class="status-label">현재 상태</div>
            <div class="status-active">
                ✅ 손들기 감지!
            </div>
            <div class="status-sub">
                (2초 이상 유지 중)
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="status-card">
            <div class="status-label">현재 출석 인원</div>
            <div class="attendance-count">
                5명
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 버튼
    btn1, btn2 = st.columns(2)

    with btn1:
        st.button(
            "▶ 출석 시작",
            use_container_width=True
        )

    with btn2:
        st.button(
            "■ 출석 종료",
            use_container_width=True
        )

    # 시스템 메시지
    st.html("""
    <div class="message-card">

        <div class="message-title">
            시스템 메시지
        </div>

        <div class="message-content">
            15:01:25 김OO 학생이 출석 완료되었습니다.
        </div>

    </div>
    """)

# =========================================================
# 실시간 출석 페이지
# =========================================================
elif page == "⏱ 실시간 출석":

    st.markdown(
        """
        <div class="attendance-card">
            <div class="attendance-header">
                <h2>출석 현황</h2>
                <span class="refresh-icon">🔄</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 통계 카드
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="stat-box blue">
                <div class="stat-title">총 수업 인원</div>
                <div class="stat-value">30명</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="stat-box green">
                <div class="stat-title">현재 출석 인원</div>
                <div class="stat-value">5명</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
            <div class="stat-box orange">
                <div class="stat-title">출석률</div>
                <div class="stat-value">83%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 출석자 목록")

    attendance_df = pd.DataFrame({
        "순번":[1,2,3,4,5],
        "이름":["김OO","이OO","박OO","최OO","정OO"],
        "출석 시간":[
            "15:01:11",
            "15:01:18",
            "15:01:25",
            "15:01:32",
            "15:01:40"
        ]
    })

    st.dataframe(
        attendance_df,
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# 학생 관리 페이지
# =========================================================
elif page == "👨‍🎓 학생 관리":

    col1, col2 = st.columns(2)

    # =========================
    # 학생 등록
    # =========================
    with col1:

        with stylable_container(
            key="register_card",
            css_styles=CARD_STYLE
        ):

            st.subheader("➕ 학생 등록")

            name = st.text_input(
                "학생 이름",
                placeholder="이름 입력"
            )

            student_id = st.text_input(
                "학번",
                placeholder="학번 입력"
            )

            student_class = st.selectbox(
                "반",
                ["A반", "B반", "C반"]
            )

            memo = st.text_area(
                "비고",
                placeholder="메모 입력"
            )

            st.button(
                "➕ 학생 등록",
                use_container_width=True
            )

    # =========================
    # 선택 학생 정보
    # =========================
    with col2:

        with stylable_container(
            key="student_info_card",
            css_styles=CARD_STYLE
        ):

            st.subheader("👤 선택 학생 정보")

            selected_student = st.selectbox(
                "학생 선택",
                [
                    "김철수",
                    "이영희",
                    "박민수",
                    "최지우",
                    "정하늘"
                ]
            )

            edit_name = st.text_input(
                "이름",
                value=selected_student,
                key="edit_name"
            )

            edit_class = st.selectbox(
                "반",
                ["A반", "B반", "C반"],
                key="edit_class"
            )

            edit_memo = st.text_area(
                "비고",
                value="학생 메모",
                key="edit_memo"
            )

            btn1, btn2 = st.columns(2)

            with btn1:
                st.button(
                    "✏ 수정",
                    use_container_width=True
                )

            with btn2:
                st.button(
                    "🗑 삭제",
                    use_container_width=True
                )

    # =========================
    # 학생 목록
    # =========================

    with stylable_container(
        key="student_list_card",
        css_styles=CARD_STYLE
    ):

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📋 학생 목록")

        with col2:
            search_name = st.text_input(
                "",
                placeholder="🔍 이름 검색",
                label_visibility="collapsed"
            )

        student_df = pd.DataFrame({
            "학번":[1,2,3,4,5],
            "이름":["김철수","이영희","박민수","최지우","정하늘"],
            "반":["A반","A반","B반","B반","C반"],
            "출석 상태":[
                "출석 완료",
                "출석 완료",
                "출석 완료",
                "손들기 감지",
                "미출석"
            ],
            "참여도":[95,85,80,70,40]
        })

        if search_name:
            student_df = student_df[
                student_df["이름"].str.contains(
                    search_name,
                    case=False
                )
            ]

        st.dataframe(
            student_df,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# 퀴즈 모드 페이지
# =========================================================
elif page == "📝 퀴즈 모드":

    st.title("퀴즈 모드")

# =========================================================
# 참여도 분석 페이지
# =========================================================
elif page == "📈 참여도 분석":

    # 학생별 참여도 순위
    participation_df = pd.DataFrame({
        "이름":["김철수","이영희","박민수","최지우","정하늘"],
        "참여도":[95,85,80,70,40]
    })

    fig_bar = px.bar(
        participation_df,
        x="참여도",
        y="이름",
        orientation="h",
        title="🏆 참여도 순위",
        text="참여도"
    )

    fig_bar.update_layout(
        height=420,
        yaxis={"categoryorder":"total ascending"},
        template="plotly_white",

        font=dict(
            color="#111827",
            size=14
        ),

        title_font=dict(
            size=22,
            color="#111827"
        ),

        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    fig_bar.update_xaxes(
        tickfont=dict(color="#111827", size=13),
        title_font=dict(color="#111827", size=15)
    )

    fig_bar.update_yaxes(
        tickfont=dict(color="#111827", size=13),
        title_font=dict(color="#111827", size=15)
    )

    # 출석 상태 비율
    status_df = pd.DataFrame({
        "상태":["출석 완료","손들기 감지","미출석"],
        "인원":[3,1,1]
    })

    fig_pie = px.pie(
        status_df,
        names="상태",
        values="인원",
        hole=0.5,
        title="📊 출석 상태 비율"
    )

    fig_pie.update_layout(
        height=420,
        template="plotly_white",

        font=dict(
            color="#111827",
            size=14
        ),

        title_font=dict(
            size=22,
            color="#111827"
        ),

        paper_bgcolor="white",

        legend=dict(
            font=dict(
                color="#111827",
                size=13
            )
        )
    )

    fig_pie.update_traces(
        marker=dict(
            colors=[
                "#6366F1",
                "#8B5CF6",
                "#C4B5FD"
            ]
        )
    )

    # 참여도 추이
    trend_df = pd.DataFrame({
        "시간":[
            "1교시",
            "2교시",
            "3교시",
            "4교시",
            "5교시"
        ],
        "평균 참여도":[
            45,
            58,
            72,
            80,
            88
        ]
    })

    fig_line = px.line(
        trend_df,
        x="시간",
        y="평균 참여도",
        markers=True,
        title="📈 평균 참여도 추이"
    )

    fig_line.update_layout(
        height=420,
        template="plotly_white",

        font=dict(
            color="#111827",
            size=14
        ),

        title_font=dict(
            size=22,
            color="#111827"
        ),

        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    fig_line.update_xaxes(
        tickfont=dict(color="#111827", size=13),
        title_font=dict(color="#111827", size=15)
    )

    fig_line.update_yaxes(
        tickfont=dict(color="#111827", size=13),
        title_font=dict(color="#111827", size=15)
    )

    col1, col2 = st.columns(2)

    with col1:
        with stylable_container(
            key="bar_chart_card",
            css_styles=CARD_STYLE
        ):
            st.plotly_chart(
                fig_bar,
                use_container_width=True,
                key="bar"
            )

    with col2:
        with stylable_container(
            key="pie_chart_card",
            css_styles=CARD_STYLE
        ):
            st.plotly_chart(
                fig_pie,
                use_container_width=True,
                key="pie"
            )

    with stylable_container(
        key="line_chart_card",
        css_styles=CARD_STYLE
    ):
        st.plotly_chart(
            fig_line,
            use_container_width=True,
            key="line"
        )