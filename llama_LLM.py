import ollama

def response(first, second, third):
    try:
        messages = [
            {
                'role': 'user',
                'content': '내가 메이저 카드 22장으로 타로를 보려고 하는데 내가 뽑은 3장의 카드를 알려줄거야. 너는 이제 그 카드들에 과거, 현재, 미래로 타로를 봐주고 markdown으로 결과를 알려줘',
            }
        ]
        
        messages.append(
            {
                'role' : 'user',
                'content' : f'{first}, {second}, {third}',
            }
        )
        
        response = ollama.chat(
            model='llama3.1:8b',
            messages=messages,
        )
        return response['message']['content']
    except Exception as e:
        print(e)