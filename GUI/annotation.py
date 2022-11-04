import psycopg2
from preprocessing import *
# from configparser import ConfigParser

# def config():
#     parser = ConfigParser()
#     parser.read()

def connect():
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="s9e0m5b8a-!"
        )

        cur = conn.cursor()

        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        db_version = cur.fetchone()
        print(db_version)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            print('Database is connected.\n')
            return conn
            # conn.close()
            # print('Database connection closed.')


# Scan Methods

# Sequential Scan
def seq_scan_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because there is no index created on the tables."""

# Index Scan
def index_scan_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because there is an index on the tables and an index scan has 
            lower cost compared to a sequential scan."""

# Index-Only Scan
def index_only_scan_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because only one attribute is selected for display."""

# Bitmap Scan
def bitmap_scan_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because the number of record schosen are too much for the index 
            scan and too little for the sequential scan."""


# Join Methods

# Nested Loop Join
def nl_join_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because the join clause is '<' OR there is no join clause."""

# Merge Join
def merge_join_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because both tables are sorted and the join clause is '='."""

# Hash Join
def hash_join_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because a hash table has been created on one of the tables."""

# Miscellaneous Operations

# Hash
def hash_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because the table is the smaller table so minimal memory is 
            required to store the hash table in memory."""

# Sort
def sort_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because a merge-join operation will be done later in the query 
            plan."""

# Aggregate
def aggregate_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because there is an aggregate function COUNT, SUM, AVG, MAX or MIN
             in this query."""

# Hash Aggregate
def hash_aggregate_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because there is a GROUP BY clause in the query and the tables are
             unsorted."""

# Group Aggregate
def group_aggregate_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because there is a GROUP BY clause and the tables are sorted."""

# Limit
def limit_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because there is a limit/offset clause in the SELECT query."""

# Unique
def unique_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because the query requires a distinct value to be take from the 
            result and it has a lower cost than Hash Aggregate or Group 
            Aggregate."""

# Append
def append_ann(query_plan):
    return f"""The {query_plan['Node Type']} operation is performed here 
            because multiple results are combined into one."""

# SetOp

# refer to https://severalnines.com/blog/overview-various-auxiliary-plan-nodes-postgresql/


conn = connect()
cur = conn.cursor()

filename = 'Queries\q3.sql'

fd = open(filename, 'r')
sqlquery = fd.read()
fd.close()

node_types_d = {}
query_plans = []

# Getting query plan
cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + sqlquery)
rows = cur.fetchall()
node_types = process_QEP(rows, query_plans, node_types_d)[0]
print()

# Getting AQPs
fetch_AQPS(cur, node_types.keys(), sqlquery, query_plans)
print("\nTotal number of query plans: " + str(len(query_plans)))

cur.close()
conn.close()
print('Database is disconnected.')

# results I got
# Connecting to the PostgreSQL database...
# PostgreSQL database version:
# ('PostgreSQL 15.0, compiled by Visual C++ build 1914, 64-bit',)
# Database is connected.

# Execution Time: 805.045
# {'Sort': 2, 'Aggregate': 2, 'Gather Merge': 1, 'Nested Loop': 1, 'Hash Join': 1, 'Seq Scan': 2, 'Hash': 1, 'Index Scan': 1}
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Gather Merge'  <- '4)Aggregate'  <- '5)Sort'  <- '6)Nested Loop'  <- '7)Hash Join'  <- '8)Seq Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Gather Merge'  <- '4)Aggregate'  <- '5)Sort'  <- '6)Nested Loop'  <- '7)Hash Join'  <- '8)Hash'  <- '9)Seq Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Gather Merge'  <- '4)Aggregate'  <- '5)Sort'  <- '6)Nested Loop'  <- '7)Index Scan';"]

# Execution Time: 691.148
# ['Sort', 'Aggregate', 'Gather', 'Nested Loop', 'Hash Join', 'Seq Scan', 'Hash', 'Seq Scan', 'Index Scan']
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Gather'  <- '4)Nested Loop'  <- '5)Hash Join'  <- '6)Seq Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Gather'  <- '4)Nested Loop'  <- '5)Hash Join'  <- '6)Hash'  <- '7)Seq Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Gather'  <- '4)Nested Loop'  <- '5)Index Scan';"]
# Execution Time: 1495.678
# ['Sort', 'Aggregate', 'Gather Merge', 'Aggregate', 'Incremental Sort', 'Nested Loop', 'Nested Loop', 'Index Scan', 'Memoize', 'Index Scan', 'Index Scan']
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Gather Merge'  <- '4)Aggregate'  <- '5)Incremental Sort'  <- '6)Nested Loop'  <- '7)Nested Loop'  <- '8)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Gather Merge'  <- '4)Aggregate'  <- '5)Incremental Sort'  <- '6)Nested Loop'  <- '7)Nested Loop'  <- '8)Memoize'  <- '9)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Gather Merge'  <- '4)Aggregate'  <- '5)Incremental Sort'  <- '6)Nested Loop'  <- '7)Index Scan';"]
# Execution Time: 1817.643
# ['Sort', 'Aggregate', 'Incremental Sort', 'Nested Loop', 'Nested Loop', 'Index Scan', 'Memoize', 'Index Scan', 'Index Scan']
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Nested Loop'  <- '5)Nested Loop'  <- '6)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Nested Loop'  <- '5)Nested Loop'  <- '6)Memoize'  <- '7)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Nested Loop'  <- '5)Index Scan';"]
# Execution Time: 4047.264
# ['Sort', 'Aggregate', 'Incremental Sort', 'Merge Join', 'Nested Loop', 'Index Scan', 'Memoize', 'Index Scan', 'Index Scan']
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Nested Loop'  <- '6)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Nested Loop'  <- '6)Memoize'  <- '7)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Index Scan';"]
# Execution Time: 4074.071
# ['Sort', 'Aggregate', 'Incremental Sort', 'Merge Join', 'Nested Loop', 'Index Scan', 'Memoize', 'Index Scan', 'Index Scan']
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Nested Loop'  <- '6)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Nested Loop'  <- '6)Memoize'  <- '7)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Index Scan';"]
# Execution Time: 3999.737
# ['Sort', 'Aggregate', 'Incremental Sort', 'Merge Join', 'Nested Loop', 'Index Scan', 'Memoize', 'Index Scan', 'Index Scan']
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Nested Loop'  <- '6)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Nested Loop'  <- '6)Memoize'  <- '7)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Merge Join'  <- '5)Index Scan';"]
# Execution Time: 2124.605
# ['Sort', 'Aggregate', 'Incremental Sort', 'Nested Loop', 'Nested Loop', 'Index Scan', 'Memoize', 'Bitmap Heap Scan', 'Bitmap Index Scan', 'Bitmap Heap Scan', 'Bitmap Index Scan']
# ["'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Nested Loop'  <- '5)Nested Loop'  <- '6)Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Nested Loop'  <- '5)Nested Loop'  <- '6)Memoize'  <- '7)Bitmap Heap Scan'  <- '8)Bitmap Index Scan';", "'1)Sort'  <- '2)Aggregate'  <- '3)Incremental Sort'  <- '4)Nested Loop'  <- '5)Bitmap Heap Scan'  <- '6)Bitmap Index Scan';"]
# Total number of query plans: 8
# Database is disconnected.

# to find out:
# what is memoize
# wy are there more than one pathway for a query plan