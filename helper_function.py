import sqlite3
import numpy as np
import urllib2
import datetime


sql_create_phish_table = """ CREATE TABLE IF NOT EXISTS phish_data (
                                        phish_id integer PRIMARY KEY,
                                        url text,
                                        phish_detail_url text,
                                        submission_time text,
                                        verification_time text,
                                        target text,
                                        online text,
                                        verified text
                                    ); """

sql_create_phish_details_table = """ CREATE TABLE IF NOT EXISTS phish_data_details (
                                    phish_id integer PRIMARY KEY,
                                    ip_address text,
                                    cidr_block text,
                                    announcing_network text,
                                    rir text,
                                    country text,
                                    detail_time text
                                ); """

sql_create_active_phish_data_table = """ CREATE TABLE IF NOT EXISTS active_phish_data (
                                    phish_id integer PRIMARY KEY
                                ); """

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
 
    return None

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def add_item_to_database(conn, item):
    try:
        conn.execute("""
        INSERT INTO phish_data (phish_id, url, phish_detail_url, submission_time, verification_time, target, online, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item['phish_id'], item['url'],item['phish_detail_url'],item['submission_time'],item['verification_time'],item['target'],item['online'],item['verified']))
        conn.execute("""
        INSERT INTO phish_data_details (phish_id, ip_address, cidr_block, announcing_network, rir, country, detail_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (item['phish_id'], item['details'][0]['ip_address'],item['details'][0]['cidr_block'],item['details'][0]['announcing_network'],item['details'][0]['rir'],item['details'][0]['country'],item['details'][0]['detail_time']))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def update_item_in_database(conn, item):
    sql = """
        UPDATE phish_data
        SET url=?, phish_detail_url=?, submission_time=?, verification_time=?, target=?, online=?, verified=?
        WHERE phish_id = ?
        """
    conn.execute(sql, (item['url'],item['phish_detail_url'],item['submission_time'],item['verification_time'],item['target'],item['online'],item['verified'],item['phish_id']))
    sql = """
        UPDATE phish_data_details
        SET ip_address=?, cidr_block=?, announcing_network=?, rir=?, country=?, detail_time=?
        WHERE phish_id = ?
        """
    conn.execute(sql, (item['details'][0]['ip_address'],item['details'][0]['cidr_block'],item['details'][0]['announcing_network'],item['details'][0]['rir'],item['details'][0]['country'],item['details'][0]['detail_time'],item['phish_id']))
    conn.commit()

def set_inactive_items_in_phish_data_table(conn):
    sql = """
        UPDATE phish_data
        SET online = 'no'
        WHERE phish_id NOT IN ( SELECT phish_id FROM active_phish_data )
        """
    conn.execute(sql)
    conn.commit()

def add_item_to_active_phish_data_table(conn, item):
    sql = """INSERT INTO active_phish_data (phish_id) VALUES (?) """
    conn.execute(sql, (item['phish_id'],))
    conn.commit()

def clear_active_phish_data_table(conn):
    sql = """DELETE FROM active_phish_data"""
    conn.execute(sql)
    conn.commit()

def check_if_item_exists(conn, item):
    try:
        return conn.execute("""SELECT phish_id FROM phish_data WHERE phish_id=?""", (item['phish_id'],)).fetchone() != None
    except sqlite3.Error as e:
        print(e)

def get_database_size(conn):
    sql = """SELECT COUNT(*) FROM phish_data"""
    return conn.execute(sql).fetchone()[0]

def get_active_phish_size(conn):
    sql = """SELECT COUNT(*) FROM active_phish_data"""
    return conn.execute(sql).fetchone()[0]

def save_webpage_snapshot(item, snapshot_dir):
    url = ''.join(item['url'])
    proj_name = ''.join(item['phish_id'])
    website_dir = snapshot_dir + '/' + proj_name
    try:

        html = urllib2.urlopen(url,timeout=1)
        with open(website_dir + ".html", "wb") as f:
            f.write(html.read())
        return True
    except:
        # print("Unable to Save phish " + proj_name)
        return False

    