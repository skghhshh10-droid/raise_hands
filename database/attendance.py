# 출석 저장 및 조회 모듈 (팀원 3 - 데이터 관리 담당)
from database.supabase_client import get_supabase_client

# Supabase 클라이언트 가져오기
supabase = get_supabase_client()

def save_attendance(name):
    """YOLO에서 이름(name)을 넘겨주면, Students 테이블에서 학번을 조회해 중복 없이 출석 저장하는 함수"""
    try:
        # 1. Students 테이블에서 넘겨받은 이름에 해당하는 학번(student_id) 찾기
        student_query = supabase.table("Students").select("student_id").eq("name", name).execute()
        
        # 등록되지 않은 이름일 때
        if len(student_query.data) == 0:
            return False
            
        student_id = student_query.data[0]["student_id"]
        
        # 2. 오늘 이미 이 학번으로 출석한 기록이 있는지 attendance 테이블에서 중복 체크
        check = supabase.table("attendance").select("*").eq("student_id", student_id).execute()
        
        # 이미 데이터가 있다면 중복이므로 False 반환
        if len(check.data) > 0:
            return False
        
        # 3. 처음 감지된 경우 attendance 테이블에 학번 최종 저장
        data = {"student_id": student_id, "status": "출석"}
        supabase.table("attendance").insert(data).execute()
        
        return True  # 출석 성공
        
    except Exception as e:
        return False  # 시스템 에러 발생 시 실패 처리

def get_attendance():
    """현재까지 출석한 전체 학생 목록을 가져오는 함수 (웹 UI 연동용)"""
    try:
        response = supabase.table("attendance").select("*").execute()
        return response.data
    except Exception as e:
        return []
