import threading
import time
from flask import Flask, request, Response
from datetime import datetime
from queue import Queue
from waitress import serve
from tele_voice import TelegramBot
from db import DatabaseManager

token = "6492881412:AAFGEg07_5wr2copGuFktJQO8VCbAO4iGRI"
AssemblyAI = "4d90c9ca19724227a3b8df944d26c93e"
app = Flask(__name__)
workQueue = Queue(maxsize=500)
thread_exit_Flag = False

class Worker(threading.Thread):
    def __init__(self, threadID, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.q = q

    def run(self):
        db_manager = DatabaseManager()
        tele = TelegramBot(token, AssemblyAI)
        while not thread_exit_Flag:
            if not self.q.empty():
                message_data = self.q.get()
                tele.process_message_content(
                    message_data["file_id"],
                    message_data["chat_id"]
                )
                db_manager.save_user_to_db(message_data["first_name"], message_data["last_name"])
            else:
                time.sleep(1)

class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.workers = []
        self.number_of_threads = 50
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            if request.method == 'POST':
                msg = request.get_json()
                current_time = datetime.now()

                if 'voice' not in msg['message']:
                    return 'No voice message'
                else:
                    chat_id = msg['message']['chat']['id']
                    message_id = msg['message']['message_id']
                    from_id = msg['message']['from']['id']
                    first_name = msg['message']['from'].get('first_name', 'Unknown')
                    last_name = msg['message']['from'].get('last_name', '')

                    voice_info = msg['message']['voice']

                    file_id = voice_info['file_id']
                    duration = voice_info['duration']
                    mime_type = voice_info.get('mime_type', 'N/A')
                    file_size = voice_info.get('file_size', 'N/A')

                    message_data = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "from_id": from_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "duration": duration,
                        "mime_type": mime_type,
                        "file_size": file_size,
                        "file_id" : file_id,
                        "current_time": current_time
                    }
                    workQueue.put(message_data)
                    return Response('ok', status=200)
            else:
                return "<h1>Welcome!</h1>"

    def start(self):
        db_manager = DatabaseManager()
        db_manager.create_table_user()
        db_manager.create_table_chat_messages()

        for i in range(self.number_of_threads):
            worker = Worker(i + 1, workQueue)
            worker.start()
            self.workers.append(worker)

        serve(self.app, host="0.0.0.0", port=8080, threads=50)

        global thread_exit_Flag
        thread_exit_Flag = True

        for worker in self.workers:
            worker.join()
        print("Exit Main Thread")

if __name__ == '__main__':
    app_instance = App()
    app_instance.start()
