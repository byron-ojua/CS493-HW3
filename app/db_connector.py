# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START cloud_sql_mysql_sqlalchemy_connect_connector]
import os

from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import logging
import sqlalchemy

logger = logging.getLogger()

db = None

# create 'businesses' table in database if it does not already exist
def create_businesses_table(db: sqlalchemy.engine.base.Engine) -> None:
    """
    Creates the 'businesses' table in the database if it does not already exist.
    """
    with db.connect() as conn:
        # Check if table exists
        result = conn.execute(sqlalchemy.text("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'businesses'
        """))
        exists = result.scalar() > 0
        if exists:
            logger.debug("Table 'businesses' already exists.")
            return
        else:
            logger.debug("Creating table 'businesses'.")

        # Create the 'businesses' table
        conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS businesses (
                business_id INT NOT NULL AUTO_INCREMENT,
                owner_id INT NOT NULL,
                name VARCHAR(50) NOT NULL,
                street_address VARCHAR(100) NOT NULL,
                city VARCHAR(50) NOT NULL,
                state CHAR(2) NOT NULL,
                zip_code INT NOT NULL,
                PRIMARY KEY (business_id)
            );
        """))
        conn.commit()

# create 'reviews' table in database if it does not already exist
def create_reviews_table(db: sqlalchemy.engine.base.Engine) -> None:
    """
    Creates the 'reviews' table in the database if it does not already exist.
    """
    with db.connect() as conn:
        # Check if table exists
        result = conn.execute(sqlalchemy.text("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'reviews'
        """))
        exists = result.scalar() > 0
        if exists:
            logger.debug("Table 'reviews' already exists.")
            return
        else:
            logger.debug("Creating table 'reviews'.")
    
        # Create the 'reviews' table
        conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id     INT           NOT NULL AUTO_INCREMENT,
                business_id   INT           NOT NULL,
                user_id       INT           NOT NULL,
                stars         INT           NOT NULL
                                    CHECK (stars BETWEEN 1 AND 5),
                review_text   VARCHAR(1000),
                
                PRIMARY KEY (review_id),
                FOREIGN KEY (business_id)
                    REFERENCES businesses(business_id)
                    ON DELETE CASCADE,
                UNIQUE KEY uniq_user_business (user_id, business_id)
            );
        """))
        conn.commit()

# initialize the database connection pool
def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = os.environ[
        "INSTANCE_CONNECTION_NAME"
    ]  # e.g. 'project:region:instance'
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # [START_EXCLUDE]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=5,
        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END_EXCLUDE]
    )
    return pool

# Sets up connection pool for the app
def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    if os.environ.get('INSTANCE_CONNECTION_NAME'):
        return connect_with_connector()
        
    raise ValueError(
        'Missing database connection type. Please define INSTANCE_CONNECTION_NAME'
    )

# Initiates connection to database
def init_db():
    """
    Initializes the database connection pool.
    """
    global db
    db = init_connection_pool()

# Create the tables if they do not exist
def create_tables():
    """
    Creates the 'businesses' and 'reviews' tables in the database if they do not
    already exist.
    """
    if db is None:
        init_db()
    create_businesses_table(db)
    create_reviews_table(db)

def get_db():
    """
    Returns the database connection pool.
    """
    if db is None:
        init_db()
    return db

# [END cloud_sql_mysql_sqlalchemy_connect_connector]
