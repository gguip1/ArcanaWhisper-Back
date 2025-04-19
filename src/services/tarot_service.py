from utils.json_loader import get_tarot_cards

tarot_cards = get_tarot_cards('./data/tarot_cards.json')

class TarotPromptService:
    def __init__(self, selected_cards:list):
        self.selected_cards = selected_cards
    
    def get_formatted_cards(self) -> str:
        formatted = []
        for card_num in self.selected_cards:
            card = tarot_cards[card_num - 1]
            name = card.get("name", "unknown")
            meaning = card.get("meaning", "의미 없음")
            formatted.append(f"- {name} ({meaning})")
        return "\n".join(formatted)
    
    def get_prompt(self) -> str:
        prompt = f"""
        (서론 없이 바로 카드 해석 시작 (출력 X))
        (필요시 자연스럽게 반말 섞어서 친근감 UP (출력x))
        
        ## 🧭 핵심 포인트 요약 (3줄)

        1. **[현재 에너지]**: 5단어 내외로 진단  
        2. **[당장 필요한 것]**: 7단어 내외 조언  
        3. **[경고 사항]**: 7단어 내외 주의점

        ---

        ## 🪄 각 카드의 숨겨진 메시지

        [카드 이름]  
        - **좋은 신호**: 친구처럼 편하게 말하는 긍정 요소  
        - **살짝 주의**: 속삭이듯 전하는 경고 메시지  
        - **활용법**: "~하면 금방 효과 볼 수 있어요" 형식

        ---

        ## 🕰️ 흐름 읽기 (시간선)

        **▶️ 과거 → 현재 → 가까운 미래**

        - **어제의 너**: 과거의 영향력  
        - **오늘의 너**: 현재의 결정적 요인 
        - **내일의 너**: 예측 가능한 미래

        ---

        ## 🔀 카드들의 조합 케미

        - **최강 콜라보**: 시너지 카드 2장 → *"이 두 개가 같이 나오면…"*  
        - **살짝 충돌**: 상충되는 카드 → *"여기서 고민이 생길 수 있어요."*

        ---

        ## 🎯 실전 행동 매뉴얼

        ✅ **당장 할 일**  
        - **3일 안에**: 구체적인 행동 1가지 → *"이거 하나만 먼저 해보세요."*  
        - **1주일 내**: 두 번째 행동 → *"효과를 보려면 이렇게 해보세요."*

        ⛔ **절대 금지**  
        - *"[특정 행동]은 정말 안 돼요!"*  
        - *"이런 사람은 피하시고…"*

        ---

        (마지막 객관적인 평가 또는 조언으로 마무리 (출력x))
        """
        return prompt
        
    
    