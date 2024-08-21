from dotenv import load_dotenv
import os

import pymysql
import pymysql.cursors

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host = os.environ.get('DB_HOST'),
        user = os.environ.get('DB_USER'),
        password = os.environ.get('DB_PASSWORD'),
        db = os.environ.get('DB_NAME'),
        charset = "utf8",
    )

def insert_tarot_result(id, tarot_reader, tarot_type, tarot_response):
    conn = get_db_connection()
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
        
            query = 'INSERT INTO tarot(id, tarot_reader, tarot_type, tarot_response) VALUES(%s, %s, %s, %s)'
            
            cur.execute(query, (id, tarot_reader, tarot_type, tarot_response))

            conn.commit()

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # 오류 발생 시 롤백
    finally:
        conn.close()
        
def select_tarot_result(id):
    conn = get_db_connection()
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
        
            query = 'SELECT tarot_reader, tarot_type, tarot_response FROM tarot'
            
            cur.execute(query)

            datas = cur.fetchall()
            return datas

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # 오류 발생 시 롤백
    finally:
        conn.close()

def check_tarot_(id, tarot_type):
    conn = get_db_connection()
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
        
            query = 'SELECT tarot_index FROM tarot WHERE id = %s AND tarot_type = %s AND created_at >= NOW() - INTERVAL 1 MONTH'
            
            cur.execute(query)

            datas = cur.fetchall()
            return datas

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()  # 오류 발생 시 롤백
    finally:
        conn.close()