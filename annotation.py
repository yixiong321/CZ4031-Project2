import psycopg2
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
            print('Database is connected.')
            return conn
            conn.close()
            print('Database connection closed.')


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

# Group By Aggregate

# Limit

# Unique

# LockRows

# SetOp

# refer to https://severalnines.com/blog/overview-various-auxiliary-plan-nodes-postgresql/

if __name__ == '__main__':
    conn = connect()
    cur = conn.cursor()

    cur.execute("""select
	    s_acctbal,
	    s_name,
	    n_name,
	    p_partkey,
	    p_mfgr,
	    s_address,
	    s_phone,
	    s_comment
    from
        part,
        supplier,
        partsupp,
        nation,
        region
    where
        p_partkey = ps_partkey
        and s_suppkey = ps_suppkey
        and p_size = 1
        and p_type like '%:2'
        and s_nationkey = n_nationkey
        and n_regionkey = r_regionkey
        and r_name = ':3'
        and ps_supplycost = (
            select
                min(ps_supplycost)
            from
                partsupp,
                supplier,
                nation,
                region
            where
                p_partkey = ps_partkey
                and s_suppkey = ps_suppkey
                and s_nationkey = n_nationkey
                and n_regionkey = r_regionkey
                and r_name = ':3'
        )
    order by
        s_acctbal desc,
        n_name,
        s_name,
        p_partkey""")

    print("Evaluating Query...")
    results = cur.fetchall()
    print(cur.rowcount)
    print(results)

    cur.execute("""explain (format json) select
	    s_acctbal,
	    s_name,
	    n_name,
	    p_partkey,
	    p_mfgr,
	    s_address,
	    s_phone,
	    s_comment
    from
        part,
        supplier,
        partsupp,
        nation,
        region
    where
        p_partkey = ps_partkey
        and s_suppkey = ps_suppkey
        and p_size = 1
        and p_type like '%:2'
        and s_nationkey = n_nationkey
        and n_regionkey = r_regionkey
        and r_name = ':3'
        and ps_supplycost = (
            select
                min(ps_supplycost)
            from
                partsupp,
                supplier,
                nation,
                region
            where
                p_partkey = ps_partkey
                and s_suppkey = ps_suppkey
                and s_nationkey = n_nationkey
                and n_regionkey = r_regionkey
                and r_name = ':3'
        )
    order by
        s_acctbal desc,
        n_name,
        s_name,
        p_partkey""")

    cur.close()
    conn.close()
    print('Database is disconnected.')
