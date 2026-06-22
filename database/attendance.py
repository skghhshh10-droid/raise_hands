# 출석 저장 모듈 (팀원 3 - 데이터 관리 담당)
from database.supabase_client import get_supabase_client

supabase = get_supabase_client()

def save_attendance(student_id: str):
    """학생의 출석 신호가 들어왔을 때, 중복을 체크하고 DB에 저장하는 함수"""
    try:
        # 1. 오늘 날짜로 이미 이 학생이 출석 처리되었는지 중복 체크
        check = supabase.table("attendance").select("*").eq("student_id", student_id).execute()
        
        # 2. 이미 데이터가 있다면 중복이므로 추가 저장 없이 리턴
        if len(check.data) > 0:
            print(f"[{student_id}] 이미 출석 처리된 학생입니다. (중복 방지 완료)")
            return {"status": "already_marked", "message": "이미 출석 완료된 학생입니다."}
        
        # 3. 처음 감지된 경우 attendance 테이블에 출석 정보 저장
        data = {"student_id": student_id, "status": "출석"}
        response = supabase.table("attendance").insert(data).execute()
        print(f"[{student_id}] 출석 데이터가 정상적으로 저장되었습니다.")
        return {"status": "success", "data": response.data}
        
    except Exception as e:
        print(f"데이터 저장 중 에러 발생: {e}")
        return {"status": "error", "message": str(e)}

def get_attendance():
    """현재까지 출석한 전체 학생 목록을 가져오는 함수 (웹 UI 연동용)"""
    try:
        response = supabase.table("attendance").select("*").execute()
        return response.data
    except Exception as e:
        print(f"데이터 조회 중 에러 발생: {e}")
        return []
