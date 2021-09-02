"""
Created on August, 9th 2021

@author: tj
"""

import psycopg2
from psycopg2 import OperationalError


class NeoIdxDb:
    def __init__(self):
        self.my_conn = self.create_connection('neo_idx_db', 'postgres', 'postgres', 'localhost', 5432)

    def close(self):
        self.my_conn.close()

    @staticmethod
    def create_connection(db_name, db_user, db_password, db_host, db_port):
        connection = None
        try:
            connection = psycopg2.connect(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
            print("Connection to PostgreSQL DB successful")
        except OperationalError as e:
            print(f"The error '{e}' occurred")
        return connection

    def select_coin_data(self, account_id=None, wallet_id=None):
        cursor = self.my_conn.cursor()

        if account_id and wallet_id:
            sql = """
                select * from neo_idx_db.neo_idx_schema.idx_wallet_all
                where account = %s and id = %s
            """
            cursor.execute(sql, (account_id, wallet_id,))
            query_results = cursor.fetchall()
            cursor.close()
            return query_results
        else:
            sql = """
                select * from neo_idx_db.neo_idx_schema.idx_wallet_all
            """
            cursor.execute(sql)
            query_results = cursor.fetchall()
            cursor.close()
            return query_results

    def insert_coin_data(self, account_id, wallet_id, address, total_amount, raw):
        sql = """
        update neo_idx_db.neo_idx_schema.idx_wallet_all 
        set total_amount = %s, raw = %s 
        where account = %s and id = %s and address = %s
        """
        cursor = self.my_conn.cursor()
        cursor.execute(sql, (total_amount, raw, account_id, wallet_id, address,))
        self.my_conn.commit()
        cursor.close()

    def create_account(self, account_id):
        sql = """
        insert into neo_idx_db.neo_idx_schema.idx_account (id)
        values (%s);
        """
        cursor = self.my_conn.cursor()
        cursor.execute(sql, (account_id,))
        self.my_conn.commit()
        cursor.close()

    def get_account_index(self, account_id):
        sql = """
          select * from neo_idx_db.neo_idx_schema.idx_account where id = %s
        """
        cursor = self.my_conn.cursor()
        cursor.execute(sql, (account_id,))
        query_results = cursor.fetchall()
        cursor.close()
        return query_results

    def create_address(self, account_id, wallet_id, address, change, kdp):
        sql = """
         insert into neo_idx_db.neo_idx_schema.idx_wallet_all (account, id, address, change, kdp)
         values (%s, %s, %s, %s, %s);
        """
        cursor = self.my_conn.cursor()
        cursor.execute(sql, (account_id, wallet_id, address, change, kdp,))
        self.my_conn.commit()
        cursor.close()

    def get_address(self, account_id: str, wallet_id: str, change: bool):
        sql = """
        select * from neo_idx_db.neo_idx_schema.idx_wallet_all
        where account = %s and id = %s and change = %s and used = false order by count asc limit 1;
        """
        cursor = self.my_conn.cursor()
        cursor.execute(sql, (account_id, wallet_id, change))
        query_results = cursor.fetchall()
        cursor.close()
        return query_results

# db_instance = NeoIdxDb()
# db_instance.create_account("JPM_UK")
# data = db_instance.get_account_index('JPM_UK')
# print(data)
