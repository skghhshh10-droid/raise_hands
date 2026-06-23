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

    try:

        student_query = (
            supabase
            .table("Students")
            .select("student_id")
            .eq("name", name)
            .execute()
        )

        print("학생 조회:", student_query.data)

        if len(student_query.data) == 0:
            return False

        student_id = student_query.data[0]["student_id"]

        print("학번:", student_id)

        check = (
            supabase
            .table("attendance")
            .select("*")
            .eq("student_id", student_id)
            .execute()
        )

        print("출석조회:", check.data)

        if len(check.data) > 0:
            return False

        data = {
            "student_id": student_id,
            "status": "출석"
        }

        supabase.table(
            "attendance"
        ).insert(data).execute()

        print("출석 저장 성공")

        return True

    except Exception as e:

        print(
            "ATTENDANCE ERROR :",
            e
        )

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


# =========================================================

# 학생 삭제

# =========================================================

def delete_student(student_id):
    """학생 삭제"""
    
    
    try:
    
        # attendance 테이블 출석기록 삭제
        supabase.table(
            "attendance"
        ).delete().eq(
            "student_id",
            student_id
        ).execute()
    
        # Students 테이블 학생 삭제
        supabase.table(
            "Students"
        ).delete().eq(
            "student_id",
            student_id
        ).execute()
    
        return True
    
    except Exception as e:
    
        print(
            "DELETE ERROR :",
            e
        )
    
        return False
    
# =========================================================
# 출석 삭제
# =========================================================

def delete_attendance(student_id):

    try:

        supabase.table(
            "attendance"
        ).delete().eq(
            "student_id",
            student_id
        ).execute()

        return True

    except Exception as e:

        print(
            "DELETE ATTENDANCE ERROR :",
            e
        )

        return False
