import redis
import logging
import os
from crawler import fetch_from_bama
import psycopg2
from psycopg2 import sql

logger = logging.getLogger(__name__)

# PostgreSQL database configuration
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = 5432
DB_NAME = os.environ.get('POSTGRES_DB')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

# Redis configuration
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = 6379


class Database:
    def __init__(self, db_name):
        self.conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        self.cursor = self.conn.cursor()
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    def create_tables(self):
        
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS car_ad (
                    code VARCHAR(100) PRIMARY KEY,
                    url VARCHAR(255),
                    title VARCHAR(255),
                    price VARCHAR(20),
                    year VARCHAR(4),
                    mileage VARCHAR(20),
                    color VARCHAR(50),
                    body_status VARCHAR(50),
                    modified_date TIMESTAMP
                );
            """)      
              
            self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_notify (
                        user_email VARCHAR(255) PRIMARY KEY
                    );
                """)
    def insert_ad(self, values):
        # Check if the ad is already in the cache
        if not self.redis.exists(values[0]):
            # If not, insert it into the database and add it to the cache
            insert_query = sql.SQL("""
                INSERT INTO car_ad (code, url, title, price, year, mileage, color, body_status, modified_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING;
            """)
            self.cursor.execute(insert_query, values)
            self.redis.set(values[0], 1)  # Add the ad to the cache
    
    def get_ads(self):
        self.cursor.execute('''SELECT * FROM car_ad''')
        return self.cursor.fetchall()