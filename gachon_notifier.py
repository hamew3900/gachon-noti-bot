import requests
from bs4 import BeautifulSoup
import os

# --- 설정 ---
# 확인할 URL
URL = "https://www.gachon.ac.kr/kor/3104/subview.do"

# GitHub Actions Secret에서 디스코드 웹훅 URL을 가져옴
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
# ----------------------------------------------------

def get_latest_post_info():
    """웹사이트에서 공지를 제외한 가장 최신 게시글 1개의 정보를 가져옵니다."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        for tr in soup.select("tbody > tr"):
            num_tag = tr.select_one("td._artclTdNum")
            # '공지'가 아닌 숫자 ID를 가진 첫 번째 게시글을 찾으면 바로 반환
            if num_tag and num_tag.text.strip().isdigit():
                post_id = int(num_tag.text.strip())
                title_tag = tr.select_one("td.td-subject > a")
                title = title_tag.text.strip()
                link = "https://www.gachon.ac.kr" + title_tag['href']
                return {'id': post_id, 'title': title, 'link': link}
        return None # 일반 게시글이 없으면 None 반환
    except Exception as e:
        print(f"오류: 게시글 정보를 가져오는 데 실패했습니다. ({e})")
        return None

def send_discord_webhook(post):
    """디스코드 웹훅으로 알림 메시지를 보냅니다."""
    if not DISCORD_WEBHOOK_URL:
        print("오류: 디스코드 웹훅 URL이 설정되지 않았습니다.")
        return

    # 디스코드에 보낼 메시지 형식 (Embed)
    data = {
        "content": "@here 가천대학교에 새로운 학사공지가 올라왔어요!", # @here로 채널의 온라인 유저에게 알림
        "embeds": [
            {
                "title": f"📄 {post['title']}",
                "description": "자세한 내용은 링크를 클릭해 확인하세요.",
                "url": post['link'],
                "color": 15258703,  # 가천대 대표 색상 (Gachon Blue)
                "footer": {
                    "text": "가천대 학사공지 알리미 봇",
                    "icon_url": "https://www.gachon.ac.kr/images/kor/intro/img_visual_symbol.jpg"
                }
            }
        ]
    }
    
    try:
        result = requests.post(DISCORD_WEBHOOK_URL, json=data)
        result.raise_for_status()
        print("성공: 디스코드 웹훅 메시지를 발송했습니다.")
    except requests.exceptions.RequestException as e:
        print(f"오류: 디스코드 웹훅 발송에 실패했습니다. ({e})")

def main():
    print(">> 가천대 학사공지 알리미 실행 시작")
    
    last_id_file = "last_post_id.txt"
    last_seen_id = 0
    
    # 이전에 저장된 마지막 글 번호를 읽어옴
    if os.path.exists(last_id_file):
        with open(last_id_file, 'r') as f:
            try:
                last_seen_id = int(f.read().strip())
            except ValueError:
                last_seen_id = 0
    print(f"   - 마지막으로 확인한 글 번호: {last_seen_id}")

    # 최신 글 정보 가져오기
    latest_post = get_latest_post_info()
    if not latest_post:
        print(">> 실행 종료: 최신 글 정보를 가져오지 못했습니다.")
        return

    print(f"   - 현재 최신 글 번호: {latest_post['id']}")

    # 새로운 글이 올라왔는지 확인
    if latest_post['id'] > last_seen_id:
        print("   - 새로운 공지를 발견했습니다! 알림을 보냅니다.")
        send_discord_webhook(latest_post)
        
        # 확인한 최신 글 번호를 파일에 저장 (다음 실행을 위해)
        with open(last_id_file, 'w') as f:
            f.write(str(latest_post['id']))
        print(f"   - 최신 글 번호 {latest_post['id']} 를 파일에 저장했습니다.")
    else:
        print("   - 새로운 공지가 없습니다.")
    
    print(">> 알리미 실행 완료")

if __name__ == "__main__":
    main()
