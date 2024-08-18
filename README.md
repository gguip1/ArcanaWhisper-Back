# 타로

## 개발 환경 구축 및 서버 동작

1. python -m venv venv
2. venv/scripts/activate
3. pip install -r requirements.txt
4. streamlit run app.py

## 타로 카드 리소스

- https://blog.naver.com/unbend/221376410990
- resource/images/tarot_ 경로에 타로 카드 이미지 저장
- Discord 참고

## tarot_with_llm
1. llama3.1:8b 모델은 ollama 설치 후 llama3.1:8b 모델 다운로드
2. ollama 서버를 켜고 사용

## 유의 사항

- 주요 키값은 .env에 저장해서 사용해주세요.
- 수정 사항이 있으면 branch를 만들어서 수정한 후 커밋해서 푸쉬해주세요.