from supabase import create_client, Client

# Supabase 접속 정보 설정
SUPABASE_URL = "https://zuzrxchkaveeflklkcgu.supabase.co"
# ⚠️ 중요: 아래 큰따옴표 안에 내 Publishable key를 넣으세요!
SUPABASE_KEY = "sb_publishable_kPk8aqdIjuuurV1GDmRMNA_-kfLxYjd" 

def get_supabase_client() -> Client:
    """Supabase 클라이언트를 생성하여 반환하는 함수"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)