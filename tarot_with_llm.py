import ollama

def ollama_response(content, selected_card):
    try:
        messages = [
            {
                'role': 'user',
                'content': f'내가 메이저 카드 22장으로 {content}에 관한 타로를 보려고 하는데 내가 뽑은 3장의 카드를 알려줄거야. 너는 이제 그 카드들을 이용해서 {content}에 관한 타로를 봐주고 markdown으로 결과를 알려줘',
            }
        ]
        
        messages.append(
            {
                'role' : 'user',
                'content' : f'첫번째 카드 : {selected_card[0]}, 두번째 카드 : {selected_card[1]}, 세번째 카드 : {selected_card[2]}',
            }
        )
        
        response = ollama.chat(
            model='llama3.1:8b',
            messages=messages,
        )
        return response['message']['content']
    except Exception as e:
        print(e)