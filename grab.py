from helper_function import *
import sqlite3
import json
import datetime
import urllib
import os.path
from apscheduler.schedulers.blocking import BlockingScheduler



def main():
    database = "./phish.db"
    snapshot_dir = './snapshots'
    phishtank_key = 'af67ca31c261bc65fe7d1dd5c7007f4c0aabc19c9127bc34accd71218dbc7d35'
    phishtank_json_url = 'http://data.phishtank.com/data/'+phishtank_key+'/online-valid.json'

    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_phish_table)
        create_table(conn, sql_create_phish_details_table)
        create_table(conn, sql_create_active_phish_data_table)
    else:
        print("Error! cannot create the database connection.")

    phish_data = json.loads(urllib.urlopen(phishtank_json_url).read())
    #phish_data = json.load(open('./test.json'))

    clear_active_phish_data_table(conn)
    for item in phish_data:
        add_item_to_active_phish_data_table(conn, item)

        if check_if_item_exists(conn, item):
            update_item_in_database(conn, item)
        else:
            add_item_to_database(conn, item)
            save_webpage_snapshot(item, snapshot_dir)
    set_inactive_items_in_phish_data_table(conn)

    with open("./phish_tank_status.txt", "a") as f:
            f.write(str(datetime.datetime.now()) + "\t" + str(get_database_size(conn)) + " phish in database, " + str(get_active_phish_size(conn)) + " are alive.\n")
    print(str(datetime.datetime.now()) + "\t" + str(get_database_size(conn)) + " phish in database, " + str(get_active_phish_size(conn)) + " are alive.")

    conn.close()
    





sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=7200)
def timed_job():
    main()

sched.start()












# sched = BlockingScheduler()

# @sched.scheduled_job('interval', seconds=10)
# def timed_job():
#     print('This job is run every 10 seconds.')

# sched.start()

