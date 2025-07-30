import requests
import json

def broadcast_message_api(token, message):
    LINE_MESSAGING_API = 'https://api.line.me/v2/bot/message/broadcast'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    data = {
        'messages': [
            {
                'type': 'text',
                'text': message
            }
        ]
    }

    response = requests.post(LINE_MESSAGING_API, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(response.text)  # 輸出成功回應內容
    else:
        print(f"Error: {response.status_code}, {response.text}")  # 顯示錯誤訊息



def push_message_api(token, user_id, message):
    LINE_MESSAGING_API = 'https://api.line.me/v2/bot/message/push'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    data = {
        'to': user_id,
        'messages': [
            {
                'type': 'text',
                'text': message
            }
        ]
    }

    response = requests.post(LINE_MESSAGING_API, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(response.text)  # 輸出成功回應內容
    else:
        print(f"Error: {response.status_code}, {response.text}")  # 顯示錯誤訊息



# 範例使用
# token = 'YOUR_CHANNEL_ACCESS_TOKEN'  # 填入你的 Channel Access Token
# user_id = 'USER_ID'  # 填入接收訊息的用戶 ID
# message = 'Hello, this is a test message!'  # 你要發送的訊息
# push_message_api(token, user_id, message)
