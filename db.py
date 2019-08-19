import psycopg2
import psycopg2.errors
import crypto
import threading
import constants


class DB:
    def __init__(self):
        self.conn = psycopg2.connect(dbname=constants.DB_NAME,
                                     user=constants.DB_USER,
                                     password=constants.DB_PASSWORD,
                                     host=constants.DB_HOST)
        self.__cursors = dict()

        self.create_tables()

    @property
    def cursor(self):
        # get safe cursor (1 per thread)
        thread_id = threading.get_ident()
        this_cursor = self.__cursors.get(thread_id)

        if this_cursor:
            return this_cursor

        this_cursor = self.__cursors[thread_id] = self.conn.cursor()
        return this_cursor

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created TIMESTAMP DEFAULT NOW()
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                created TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL, 
                created TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')

        self.conn.commit()

    def insert_user(self, username, password):
        hashed_password = crypto.hash_password(password)

        try:
            self.cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            RETURNING id;
            ''', (username, hashed_password))
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            return

        self.conn.commit()

        user_id = self.cursor.fetchone()[0]

        return user_id

    def insert_token(self, user_id):
        token = crypto.get_new_token()
        hashed_token = crypto.hash_password(token)

        self.cursor.execute('''
            INSERT INTO tokens (user_id, token)
            VALUES (%s, %s)
            RETURNING id;
        ''', (user_id, hashed_token))
        self.conn.commit()

        token_id = self.cursor.fetchone()[0]

        return token_id, token

    def verify_user_password(self, username, password):
        self.cursor.execute('''
            SELECT id, password FROM users
            WHERE username = %s LIMIT 1;
        ''', (username,))

        result = self.cursor.fetchone()

        if not result:
            return
        
        user_id, hashed_password = result

        is_valid_password = crypto.check_password(password, hashed_password)

        if is_valid_password:
            return user_id

    def verify_user_token(self, token_id, token):
        self.cursor.execute('''
            SELECT user_id, token FROM tokens
            WHERE id = %s LIMIT 1;
        ''', (token_id,))

        result = self.cursor.fetchone()

        if not result:
            return

        user_id, hashed_token = result

        is_valid_token = crypto.check_password(token, hashed_token)

        if is_valid_token:
            return user_id

    def insert_new_message(self, user_id, text):
        self.cursor.execute('''
            INSERT INTO messages (user_id, text)
            VALUES (%s, %s)
            RETURNING id, user_id, text, extract(epoch from created) as created;
        ''', (user_id, text))

        self.conn.commit()

        return dict(zip(['id', 'user_id', 'text', 'created'], self.cursor.fetchone()))

    def select_messages(self, count):
        if type(count) is not int:
            return

        self.cursor.execute('''
            SELECT 
                messages.id as id, 
                username, 
                text, 
                extract(epoch from messages.created) as created 
            FROM messages
            LEFT JOIN users
            ON users.id = messages.user_id
            ORDER BY messages.id DESC LIMIT %s
        ''', (count,))

        return list(
            map(
                lambda message: dict(zip(['id', 'username', 'text', 'created'], message)), self.cursor.fetchall()
            )
        )

    def select_username_by_user_id(self, user_id):
        self.cursor.execute('''
            SELECT username FROM users
            WHERE id=%s LIMIT 1;
        ''', (user_id,))

        result = self.cursor.fetchone()

        if result:
            return result[0]
