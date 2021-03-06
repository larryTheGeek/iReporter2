import psycopg2
from flask import current_app
from psycopg2.extras import RealDictCursor


class Db:
    def __init__(self):

        self.database_url = current_app.config['DATABASE_URL']
        self.connect = psycopg2.connect(self.database_url)
        self.cursor = self.connect.cursor(cursor_factory=RealDictCursor)

    def init_app(self, app):
        self.connect = psycopg2.connect(app.config['DATABASE_URL'])
        self.cursor = self.connect.cursor(cursor_factory=RealDictCursor)

    def create_tables(self):
        users = """CREATE TABLE IF NOT EXISTS users(
            user_id serial PRIMARY KEY NOT NULL,
            first_name character varying(100) NOT NULL,
            last_name character varying(100) NOT NULL,
            username character varying(100) NOT NULL,
            email character varying(100) NOT NULL,
            date_created timestamp with time zone DEFAULT ('now'::text):: date NOT NULL,
            phonenumber character varying(10) NOT NULL,
            password character varying(150) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
            )"""
        incidents = """CREATE TABLE IF NOT EXISTS incidents (
            incident_id serial PRIMARY KEY NOT NULL,
            created_by integer NOT NULL references users (user_id),
            type character varying(20) NOT NULL,
            description character varying (200) NOT NULL,
            status character varying(20) DEFAULT 'DRAFT',
            location character varying(50) NOT NULL,
            media_path character varying(40),
            created_on timestamp with time zone DEFAULT ('now'::text):: date NOT NULL
        )"""
        queries = [users, incidents]
        for query in queries:
            self.cursor.execute(query)
        self.connect.commit()

    def destroy_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS incidents")
        self.cursor.execute("DROP TABLE IF EXISTS users")
        self.connect.commit()
        self.connect.commit()
        self.connect.close()
