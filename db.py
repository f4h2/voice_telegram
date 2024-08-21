import psycopg2
import psycopg2.extras
from datetime import datetime

class DatabaseManager:
    def __init__(self, hostname='localhost', database='Telegram_voice_2002', username='postgres', password='12345678', port_id=5432):
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.port_id = port_id

    def get_db_connection(self):
        return psycopg2.connect(
            host=self.hostname,
            dbname=self.database,
            user=self.username,
            password=self.password,
            port=self.port_id
        )

    def create_table_chat_messages(self):
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                create_table_script = '''
                    CREATE TABLE IF NOT EXISTS chatMessages (
                        id SERIAL PRIMARY KEY,
                        audio_url TEXT NOT NULL,
                        textx TEXT NOT NULL,
                        gia_tri_camxuc TEXT NOT NULL,
                        current_timex TIMESTAMP
                    )
                '''
                cur.execute(create_table_script)
            conn.commit()
        except Exception as error:
            print(f"Error creating table: {error}")
        finally:
            if conn is not None:
                conn.close()

    def save_message_to_db_message(self, audio_url,textx, gia_tri_camxuc, current_timex):
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                insert_script = '''
                    INSERT INTO chatMessages (audio_url,textx, gia_tri_camxuc, current_timex)
                    VALUES (%s, %s,%s, %s)
                '''
                cur.execute(insert_script, (audio_url,textx, gia_tri_camxuc, current_timex))
            conn.commit()
        except Exception as error:
            print(f"Error saving message: {error}")
        finally:
            if conn is not None:
                conn.close()

    def create_table_user(self):
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                create_table_script = '''
                    CREATE TABLE IF NOT EXISTS InfoUser (
                        id SERIAL PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL
                    )
                '''
                cur.execute(create_table_script)
            conn.commit()
        except Exception as error:
            print(f"Error creating table: {error}")
        finally:
            if conn is not None:
                conn.close()

    def user_exists(self, first_name, last_name):
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                select_script = '''
                    SELECT * FROM InfoUser
                    WHERE first_name = %s AND last_name = %s
                '''
                cur.execute(select_script, (first_name, last_name))
                user = cur.fetchone()
                return user is not None
        except Exception as error:
            print(error)
            return False
        finally:
            if conn is not None:
                conn.close()

    def save_user_to_db(self, first_name, last_name):
        if self.user_exists(first_name, last_name):
            print(f"User {first_name} {last_name} already exists.")
            return
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                insert_script = '''
                    INSERT INTO InfoUser (first_name, last_name)
                    VALUES (%s, %s)
                '''
                cur.execute(insert_script, (first_name, last_name))
            conn.commit()
        except Exception as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
