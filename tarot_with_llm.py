import ollama
import json
import boto3

# 메이저 아르카나 카드 의미
CARD_MEANINGS = {
    'The Fool': '새로운 시작, 순수함, 모험',
    'The Magician': '창조력, 자원, 집중력',
    'The High Priestess': '지혜, 비밀, 직관',
    'The Empress': '풍요, 창조성, 어머니의 에너지',
    'The Emperor': '권위, 통제, 안정성',
    'The Hierophant': '전통, 신앙, 도덕적 가치',
    'The Lovers': '사랑, 관계, 선택',
    'The Chariot': '승리, 의지, 결단력',
    'Strength': '내적 힘, 용기, 인내',
    'The Hermit': '내성, 고독, 명상',
    'Wheel of Fortune': '운명, 변화, 행운',
    'Justice': '정의, 균형, 책임',
    'The Hanged Man': '희생, 새로운 관점, 중지',
    'Death': '변화, 종말, 새 출발',
    'Temperance': '조화, 절제, 중용',
    'The Devil': '유혹, 물질적 집착, 속박',
    'The Tower': '돌발적 변화, 붕괴, 해방',
    'The Star': '희망, 영감, 치유',
    'The Moon': '환상, 직관, 무의식',
    'The Sun': '행복, 성공, 긍정성',
    'Judgement': '자기 성찰, 부활, 갱신',
    'The World': '성취, 완성, 통합',
}

def generate_daily_fortune(selected_cards):
    meanings = [CARD_MEANINGS.get(card, '알 수 없는 카드입니다.') for card in selected_cards]
    overall_reading = f"오늘의 운세는 '{selected_cards[0]}', '{selected_cards[1]}', '{selected_cards[2]}' 카드를 기반으로 합니다. 이 카드들은 각각 '{meanings[0]}', '{meanings[1]}', '{meanings[2]}'를 의미하며, 이를 바탕으로 오늘 하루는 {meanings[0]}, {meanings[1]}, {meanings[2]}의 요소들이 중요한 역할을 할 것입니다."
    return overall_reading

def ollama_response(content, selected_card):
    try:
        daily_fortune = generate_daily_fortune(selected_card)
        return daily_fortune
    except Exception as e:
        print(e)
        return "에러가 발생했습니다."

def sonnet_respone(content, selected_card):
    bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    try:
        daily_fortune = generate_daily_fortune(selected_card)
        return daily_fortune
    except Exception as e:
        print(e)
        return "에러가 발생했습니다."
