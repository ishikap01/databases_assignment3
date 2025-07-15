# utils.py
import mysql.connector
import os
import logging
from datetime import datetime
import os
from urllib.parse import urlparse


# Database configurations
db_config_proj = {
     "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT"))
}

db_config_cism = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT"))
}


import mysql.connector

def get_db_connection(cims=True):
    if cims:
        db_url = os.getenv("DATABASE_URL")  # This will be set in Render
        if not db_url:
            raise Exception("DATABASE_URL not found in environment variables")

        result = urlparse(db_url)

        return mysql.connector.connect(
            host=result.hostname,
            port=result.port,
            user=result.username,
            password=result.password,
            database=result.path[1:]  # Skip leading slash in '/dbname'
        )
    else:
        # (Optional) If you still use your local or second project DB
        return mysql.connector.connect(
            host="10.0.116.125",
            user="cs432g16",
            password="LbNXp7Tz",
            database="cs432g16"
        )



def validate_session(session_token):
    try:
        conn = get_db_connection(cims=True)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT MemberID, Role, Expiry FROM Login
            WHERE Session = %s
        """, (session_token,))
        session_data = cursor.fetchone()

        if not session_data:
            return None

        if session_data['Expiry'] and int(session_data['Expiry']) > int(datetime.now().timestamp()):
            return {
                "MemberID": session_data['MemberID'],
                "Role": session_data['Role']
            }
        else:
            return None

    except mysql.connector.Error as e:
        logging.error(f"Session validation failed: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

def is_admin(session_token):
    """Return True if the session token is valid and belongs to an admin."""
    login_row = validate_session(session_token)
    if login_row and login_row.get("Role", "").lower() == "admin":
        return True
    return False

def log_change_to_db(conn, performed_by, action_type, table_name, description):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Change_Log (Timestamp, Action, MemberID, PerformedBy, Details)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datetime.now(),             # Timestamp
            f"{action_type} on {table_name}",  # Action
            None,                       # MemberID affected (optional)
            performed_by,              # PerformedBy (admin)
            description                 # Details
        ))
        conn.commit()
    finally:
        cursor.close()
import mysql.connector

import mysql.connector
import datetime

def log_change(performed_by, action_type, table_name, description):
    try:
        conn = mysql.connector.connect(
            host='10.0.116.125',
            user='cs432g16',
            password='LbNXp7Tz',
            database='cs432g16'
        )
        cursor = conn.cursor()

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = """
            INSERT INTO Change_Log (Timestamp, PerformedBy, ActionType, TableName, Description)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (timestamp, performed_by, action_type, table_name, description))
        conn.commit()

    except Exception as e:
        print(f"Logging change to DB failed: {e}")

    finally:
        cursor.close()
        conn.close()


def log_unauthorized_access(action, details):
    """Log unauthorized access attempts."""
    logging.warning(f"Unauthorized attempt for {action}: {details}")
