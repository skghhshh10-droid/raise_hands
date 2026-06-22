# [수정 완료] 파이썬 파일 안에서 에러가 나지 않도록 주석 처리했습니다.
# 터미널창에 pip install selenium requests를 따로 입력해 설치해 주세요.

# 웹 브라우저를 제어하기 위한 핵심 도구
from selenium import webdriver
# 웹 요소를 찾을 때 '어떤 방법으로' 찾을 지 (선택자)
from selenium.webdriver.common.by import By
# 코드 실행 중간에 잠시 멈추게 하기 위한 도구
import time
# 웹 페이지 이미지 URL에 접속해서 이미지 데이터를 직접 내려받기 위한 도구
import requests
# 운영체제 / 폴더를 만들기 위한 도구
import os
# 텍스트형태의 이미지 인코딩을 위한 도구
import base64

# 크롬 웹 드라이버 실행 (새로운 크롬 창이 열림)
driver = webdriver.Chrome()

# [수정] 출석체크 AI 학습을 위해 검색할 키워드 리스트 설정
search_queries = ["손들기", "hand raising", "raising hand in classroom", "손든 사람"] 

# [수정] 이미지를 저장할 메인 폴더명 설정
output_folder = "raised_hands_images"
os.makedirs(output_folder, exist_ok=True)

count = 0 # 저장된 이미지 총 개수 카운팅
max_images = 500 # 최대 몇개의 이미지를 저장할지 목표 수량 설정

# [수정 완료] 구글 차단을 차단하기 위한 브라우저 우회 봇 방지 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 여러 키워드로 반복 검색 진행
for query in search_queries:
    if count >= max_images:
        break
        
    print(f"\n📡 '{query}' 키워드로 검색을 시작합니다...")
    
    # 구글 이미지 검색 URL 생성 및 이동
    url = f"https://www.google.com/search?tbm=isch&q={query}"
    driver.get(url)
    time.sleep(2) # 페이지 로딩 대기

    # 스크롤 충분히 내리기
    for i in range(12):  
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(3) # 이미지 로딩 대기

    # class 속성이 YQ4gaf "만" 있는 이미지 선택
    thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.YQ4gaf:not([class*=' '])")
    print(f"🔍 발견된 이미지 요소 개수: {len(thumbnails)}개")

    # 수집 시작
    for img in thumbnails:
        if count >= max_images:
            break
        try:
            src = img.get_attribute("src") 

            if not src: 
                continue

            img_data = None  

            # 1. src가 http로 시작하면 requests로 다운로드
            if src.startswith(('http://', 'https://')):
                # [수정 완료] 차단 에러 방지를 위해 headers=headers를 추가했습니다.
                img_data = requests.get(src, headers=headers, timeout=5).content

            # 2. src가 data:image로 시작하면 base64로 디코딩
            elif src.startswith('data:image'):
                header, encoded_data = src.split(',', 1) 
                img_data = base64.b64decode(encoded_data) 

            # 파일로 저장
            if img_data:
                file_path = os.path.join(output_folder, f"hand_{count}.jpg")
                with open(file_path, "wb") as f:
                    f.write(img_data)

                print(f"[{count}] 저장 완료 - {file_path}")
                count += 1
                
        except Exception as e:
            pass

# 모든 작업이 끝나면 드라이버 종료
driver.quit() 
print(f"\n✨ 크롤링 완료! 총 {count}개의 손들기 이미지를 '{output_folder}' 폴더에 저장했습니다.")

