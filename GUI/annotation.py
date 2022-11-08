import psycopg2
from preprocessing import *
import pickle

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
def seq_scan_ann(plan):
    return f"""The Sequential Scan operation is performed here because there is no index created on the table {plan['Alias']}, hence it is suitable to go through the table tuple by tuple."""

# Index Scan
def index_scan_ann(plan):
    return f"""The Index Scan operation is performed here because there is an index {plan['Index Name']} on the table {plan['Alias']} and an index scan has lower cost compared to a sequential scan."""

# Index-Only Scan
def index_only_scan_ann(plan):
    return f"""The Index-Only Scan operation is performed here because only one attribute, {plan['Output']}, is needed to satisfy the query."""

# Bitmap Scan
def bitmap_scan_ann(plan):
    return f"""The Bitmap Scan operation is performed here because the number of records chosen are too many for the index scan and too few for the sequential scan."""


# Join Methods

# Nested Loop Join
def nl_join_ann(plan):
    return f"""The Nested Loop Join operation is performed here because the join clause is '<' OR there is no join clause."""

# Nested Loop Semi Join
def nl_semi_join_ann(plan):
    return f"""The Nested Loop Semi Join operation is performed here because there is an EXISTS clause in the query that requires the outer rows to be filtered by the inner rows, returning the results of the outer rows only."""

# Merge Join
def merge_join_ann(plan):
    return f"""The Merge Join operation is performed here because both tables are sorted and the join clause is '='. It has a lesser cost for the """

# Hash Join
def hash_join_ann(plan):
    return f"""The Hash Join operation is performed here because a hash table has been created on one of the tables."""

# Miscellaneous Operations

# Hash
def hash_ann(plan):
    return f"""The Hash operation is performed here because the table is the smaller table so minimal memory is required to store the hash table in memory.Here, the hash is done on the {plan['Output']}."""

# Sort
def sort_ann(plan):
    return f"""The Sort operation is performed here to sort according to {plan['Sort Key']}."""

# Incremental Sort
def incremental_sort_ann(plan):
    return f"""The Incremental Sort operation is performed here because it has a much lower cost due to the reduction in memory usage and the likelihood of spilling the sorts into disk."""

# Aggregate
def aggregate_ann(plan):
    return f"""The Aggregate operation is performed here because there is an aggregate function COUNT, SUM, AVG, MAX or MIN in this query."""

# Hash Aggregate
def hash_aggregate_ann(plan):
    return f"""The Hash Aggregate operation is performed here because there is a GROUP BY clause in the query and the tables are unsorted."""

# Group Aggregate
def group_aggregate_ann(plan):
    return f"""The Group Aggregate operation is performed here because there is a GROUP BY clause and the tables are sorted."""

# Limit
def limit_ann(plan):
    return f"""The Limit operation is performed here because there is a LIMIT/OFFSET clause in the SELECT query."""

# Unique
def unique_ann(plan):
    return f"""The Unique operation is performed here because the query requires a distinct value to be take from the result and it has a lower cost than Hash Aggregate and Group Aggregate."""

# Append
def append_ann(plan):
    return f"""The Append operation is performed here because multiple results are combined into one."""

# Gather
def gather_ann(plan):
    return f"""The Gather function is performed here because there are {plan['Workers Launched']} workers launched in child nodes and the data output from these workers need to be combined."""

# Gather Merge
def gather_merge_ann(plan):
    return f"""The Gather Merge operation is performed here because the data is sorted and the there is a need to combine the output of the child nodes."""

# Materialize
def materialize_ann(plan):
    return f"""The Materialize operation is performed here because there are only a few tuples in the output of the child node so it materializes its output into memory before passing to the next node."""

# Memoize
def memoize_ann(plan):
    return f"""The Memoize operation is performed here because there is enough available memory to cache the required rows that are have not been cached. It has a lower cost than Materialize because there are no I/O costs to the disk."""

# SetOp

# refer to https://severalnines.com/blog/overview-various-auxiliary-plan-nodes-postgresql/

# annotation_dict = {
#     "Seq Scan" : seq_scan_ann(),
#     "Index Scan" : index_scan_ann(),
#     "Index Only Scan" : index_only_scan_ann(),
#     "Bitmap Heap Scan" : bitmap_scan_ann(),
#     "Nested Loop" : nl_join_ann(),
#     "Nested Loop Semi Join" : nl_semi_join_ann,
#     "Merge Join" : merge_join_ann(),
#     "Hash Join" : hash_join_ann(),
#     "Hash" : hash_ann(),
#     "Sort" : sort_ann(),
#     "Incremental Sort" : incremental_sort_ann(),
#     "Aggregate" : aggregate_ann(),
#     "HashAggregate" : hash_aggregate_ann(),
#     "GroupAggregate" : group_aggregate_ann(),
#     "Limit" : limit_ann(),
#     "Unique" : unique_ann(),
#     "Append" : append_ann(),
#     "Gather" : gather_ann(),
#     "Gather Merge" : gather_merge_ann(),
#     "Materialize" : materialize_ann(),
#     "Memoize" : memoize_ann()
# }

# Traverse through plan and annotate respective nodes accordingly
def obtain_ann_list(query_plan):
    list_of_nodes = []
    for x in query_plan[0][0]:
        get_nodelist(x['Plan'], list_of_nodes)

    print(list_of_nodes)
    ann_list = []
    for node_name in list_of_nodes:
        if node_name in annotation_dict:
            ann_list.append(annotation_dict.get(node_name))
    return ann_list

def print_list(list):
    for element in list:
        print(element)
        print()

# Find full information on the node
def find_node_info(node_type, query_plan):
    for x in query_plan:
        # print(x['Node Type'])
        if x['Node Type'] == node_type:
            # print("found it!")
            return x
        elif 'Plans' not in x:
            # print("I'm in Plans not in x")
            continue
        else:
            # print("going into next Plans")
            node_info = find_node_info(node_type, x['Plans'])
            return node_info

def annotate(query_plan):
    level = query_plan[0][0]
    for x in level:
        if [x['Node Type'] == 'Seq Scan']:
            seq_scan_ann(x)
        elif [x['Node Type'] == 'Index Scan']:
            index_scan_ann(x)
        elif [x['Node Type'] == 'Index Only Scan']:
            index_only_scan_ann(x)
        elif [x['Node Type'] == 'Bitmap Heap Scan']:
            bitmap_scan_ann(x)
        elif [x['Node Type'] == 'Nested Loop']:
            nl_join_ann(x)
        elif [x['Node Type'] == 'Nested Loop Semi Join']:
            nl_semi_join_ann(x)
        elif [x['Node Type'] == 'Merge Join']:
            merge_join_ann(x)
        elif [x['Node Type'] == 'Hash Join']:
            hash_join_ann(x)
        elif [x['Node Type'] == 'Hash']:
            hash_ann(x)
        elif [x['Node Type'] == 'Sort']:
            sort_ann(x)
        elif [x['Node Type'] == 'Incremental Sort']:
            incremental_sort_ann(x)
        elif [x['Node Type'] == 'Aggregate']:
            aggregate_ann(x)
        elif [x['Node Type'] == 'HashAggregate']:
            hash_aggregate_ann(x)
        elif [x['Node Type'] == 'GroupAggregate']:
            group_aggregate_ann(x)
        elif [x['Node Type'] == 'Limit']:
            limit_ann(x)
        elif [x['Node Type'] == 'Unique']:
            unique_ann(x)
        elif [x['Node Type'] == 'Append']:
            append_ann(x)
        elif [x['Node Type'] == 'Gather']:
            gather_ann(x)
        elif [x['Node Type'] == 'Gather Merge']:
            gather_merge_ann(x)
        elif [x['Node Type'] == 'Materialize']:
            materialize_ann(x)
        elif [x['Node Type'] == 'Memoize']:
            memoize_ann(x)

        level = level['Plans']


conn = connect()
cur = conn.cursor()

filename = 'GUI\Queries\q6.sql'

fd = open(filename, 'r')
sqlquery = fd.read()
fd.close()

node_types_d = {}
query_plans = []

# Getting query plan
cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + sqlquery)
plan = cur.fetchall()
# print(plan)
# node_types = process_QEP(plan, query_plans, node_types_d)[0]
print()

# Getting the list of annotations corresponding to the nodes
# ann_list = obtain_ann_list(plan)
# print_list(ann_list)

# Getting QEP + AQPs
with open('query_plans'+'6'+'.pkl', 'rb') as f:
    list_of_plans = pickle.load(f)

node_type = 'Bitmap Heap Scan'
if list_of_plans[1]['Plan']['Node Type'] == node_type:
    x = list_of_plans[1]['Plan']
else:
    x = find_node_info(node_type, list_of_plans[1]['Plan']['Plans'])
print(x)
# fetch_AQPS(cur, node_types.keys(), sqlquery, query_plans)
# print("\nTotal number of query plans: " + str(len(query_plans)))

cur.close()
conn.close()
print('Database is disconnected.')