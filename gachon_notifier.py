def main():
    # --- 디스코드 전송 기능만 테스트 ---
    print(">> 디스코드 웹훅 전송 테스트 시작")

    # 가짜 게시글 정보 생성
    test_post = {
        'id': 9999,
        'title': '이것은 테스트 공지입니다',
        'link': 'https://www.gachon.ac.kr/kor/3104/subview.do'
    }

    # 디스코드 전송 함수 직접 호출
    send_discord_webhook(test_post)

    print(">> 테스트 종료")


if __name__ == "__main__":
    main()
