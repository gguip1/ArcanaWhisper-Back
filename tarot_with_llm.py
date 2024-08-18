import ollama

import json
import boto3

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

def sonnet_respone(content, selected_card):
    bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    try:
        messages = [
            {
                'role': 'user',
                'content': [{"type": "text", "text": f'내가 메이저 카드 22장으로 {content}에 관한 타로를 보려고 하는데 내가 뽑은 3장의 카드를 알려줄거야. 너는 이제 그 카드들을 이용해서 {content}에 관한 타로를 봐주고 markdown으로 결과만 알려줘'}],
            }
        ]
        
        messages.append(
            {
                'role': 'assistant',
                'content': [{"type": "text", "text": f'저는 타로 마스터입니다. 뽑으신 3가지 카드를 알려주세요. markdown으로 결과만 알려드리겠습니다.'}]
            }
        )
        
        messages.append(
            {
                'role': 'user',
                'content': [{"type": "text", "text": f'첫번째 카드 : {selected_card[0]}, 두번째 카드 : {selected_card[1]}, 세번째 카드 : {selected_card[2]}'}],
            }
        )
        
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": messages,
            }
        )
        
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body,
        )
        
        response_body = json.loads(response.get("body").read())
        
        return response_body["content"][0]["text"]
    except Exception as e:
        print(e)