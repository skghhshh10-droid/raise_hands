# =========================================================
# 출석 저장 및 조회 모듈
# =========================================================

from database.supabase_client import get_supabase_client

# Supabase 클라이언트
supabase = get_supabase_client()


# =========================================================
# 학생 등록
# =========================================================

def register_student(student_id, name):
    """Students 테이블에 학생 등록"""

    try:

        # 중복 학번 확인
        check = (
            supabase
            .table("Students")
            .select("*")
            .eq("student_id", student_id)
            .execute()
        )

        if len(check.data) > 0:
            return False

        data = {
            "student_id": student_id,
            "name": name
        }

        supabase.table(
            "Students"
        ).insert(data).execute()

        return True

    except Exception as e:

        print("REGISTER ERROR :", e)

        return False


# =========================================================
# 출석 저장
# =========================================================

def save_attendance(name):
    """
    학생 이름으로 Students 테이블 조회 후
    attendance 테이블에 출석 저장
    """

    try:

        # 학생 조회
        student_query = (
            supabase
            .table("Students")
            .select("student_id")
            .eq("name", name)
            .execute()
        )

        if len(student_query.data) == 0:
            print("학생이 등록되어 있지 않습니다.")
            return False

        student_id = student_query.data[0]["student_id"]

        # 중복 출석 확인
        check = (
            supabase
            .table("attendance")
            .select("*")
            .eq("student_id", student_id)
            .execute()
        )

        if len(check.data) > 0:
            print("이미 출석한 학생입니다.")
            return False

        data = {
            "student_id": student_id,
            "status": "출석"
        }

        supabase.table(
            "attendance"
        ).insert(data).execute()

        return True

    except Exception as e:

        print("ATTENDANCE ERROR :", e)

        return False


# =========================================================
# 출석 조회
# =========================================================

def get_attendance():
    """attendance 테이블 조회"""

    try:

        response = (
            supabase
            .table("attendance")
            .select("*")
            .execute()
        )

        return response.data

    except Exception as e:

        print("GET ATTENDANCE ERROR :", e)

        return []


# =========================================================
# 학생 조회
# =========================================================

def get_students():
    """Students 테이블 조회"""

    try:

        response = (
            supabase
            .table("Students")
            .select("*")
            .execute()
        )

        return response.data

    except Exception as e:

        print("GET STUDENTS ERROR :", e)

        return []