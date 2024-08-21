import time
from datetime import datetime

import requests
from credentials import *

from db import DatabaseManager


class TelegramBot:
    def __init__(self, bot_token,AssemblyAI ):
        self.bot_token = bot_token
        self.AssemblyAI = AssemblyAI

    def _send_request(self, method, payload):
        url = f'https://api.telegram.org/bot{self.bot_token}/{method}'
        response = requests.post(url, json=payload)
        return response
    def tel_send_message(self, chat_id, text):
        payload = {'chat_id': chat_id, 'text': text}
        return self._send_request('sendMessage', payload)

    def process_message_content(self, file_id,chat_id):
        current_time = datetime.now().isoformat()
        database = DatabaseManager()
        url = f"https://api.telegram.org/bot{self.bot_token}/getFile?file_id={file_id}"
        telegram_filepath = requests.get(url).json()['result']['file_path']

        # Telegram voice message public URL
        audio_url = f'https://api.telegram.org/file/bot{self.bot_token}/{telegram_filepath}'

        mime_type = requests.head(audio_url).headers.get('Content-Type')
        print(f"Detected mime type: {mime_type}")
        # if mime_type not in ['audio/ogg', 'audio/wav']:
        #     print("Unsupported file type.")
        #     return

        # AssemblyAI transcript endpoints
        transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
        polling_endpoint = "https://api.assemblyai.com/v2/transcript/"

        # Set headers for AssemblyAI requests
        header = {
            'authorization': self.AssemblyAI,
            'content-type': 'application/json'
        }

        # Prepare the request for AssemblyAI
        transcript_request = {
            'audio_url': audio_url,
            'sentiment_analysis': True
        }

        # Send voice message to AssemblyAI
        transcript_response = requests.post(
            transcript_endpoint,
            json=transcript_request,
            headers=header
        )
        print(transcript_response)
        # Wait for transcript completion by polling AssemblyAI
        while True:
            print("Polling...")
            polling_response = requests.get(polling_endpoint + transcript_response.json()['id'], headers=header)
            polling_response = polling_response.json()
            if polling_response['status'] == 'completed':
                break
            time.sleep(3)
            # print(polling_response)
        t = 0
        if 'sentiment_analysis_results' in polling_response and polling_response['sentiment_analysis_results']:
            for result in polling_response['sentiment_analysis_results']:
                gia_tri_camxuc = result["sentiment"]
                textx =  result["text"]
                print(gia_tri_camxuc)

                self.tel_send_message(chat_id, f"Câu {t+1 }: có cảm xúc")
                self.tel_send_message(chat_id, gia_tri_camxuc)
                database.save_message_to_db_message(audio_url,textx, gia_tri_camxuc, current_time)
                t+=1
        else:
            print("Sentiment analysis results not found in response.")


