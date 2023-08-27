import sqlite3


# Table User_id request count_views
if __name__ == '__main__':
    conn = sqlite3.connect('tracking_requests.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users_requests
                    (id INTEGER PRIMARY KEY,
                    telegram_id INTEGER,
                    user_name TEXT,
                    number_requests TEXT,
                    len_result INTEGER DEFAULT 0 NOT NULL, 
                    count_file INTEGER DEFAULT 0 NOT NULL,
                    date TEXT)''')
    conn.close()

if __name__ == '__main__':
    conn = sqlite3.connect('tracking_requests.db')
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM users_requests''')
    conn.commit()
    conn.close()
