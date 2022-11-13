import psycopg2
from preprocessing import *
import pickle
import sqlparse

def connect():
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
                host="localhost",
                database="TPC-H",
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

def splitQuery(query):
    sql_keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY','ORDER BY', 'EXISTS', 'LIMIT', 'DISTINCT']
    list1 = []
    list2 = []

    #make SQL keywords capital
    res = sqlparse.format(query, encoding=None, keyword_case = "upper")

    parsed = sqlparse.parse(res)
    stmt = parsed[0]
    for i in stmt.tokens:
        list1.append(str(i)) #list1 has all the tokens generated by sqlparse

    row = 0
    for i in list1:
        #print("iteration for " + i)
        if i in sql_keywords and row == 0:
            list2.append(i)
            row+=1        
        
        elif i not in sql_keywords:
            if 'WHERE' in i.split(None):
                row+=1
                list2.append(i)
            else: list2[row-1] += i
        
        elif i in sql_keywords and row != 0:
            row+=1
            list2.append(i)
        #print(list2)
    
    return list2

def format(string):
    if '(' == string[0]:
        string = string[1:-1]
    if '::date' in string:
        string = string.replace('::date', '')
    if '::numeric' in string:
        string = string.replace('::numeric', '')
    if 'PARTIAL ' in string:
        string = string.replace('PARTIAL ', '')
    if '::bpchar' in string:
        string = string.replace('::bpchar', '')
    
    return string

# SCAN OPERATORS

# Sequential Scan
def seq_scan_ann(plan):
    if 'Filter' in plan:
        cond = plan['Filter']
        condd = format(cond)
        return f"""The Sequential Scan operation is performed here because there is no index created on the table {plan['Alias']}, hence the only way is to go through the table tuple by tuple. Tuples that do not satisfy {condd} are removed from the output."""
    return f"""The Sequential Scan operation is performed here because there is no index created on the table {plan['Alias']}, hence the only way is to go through the table tuple by tuple."""

# Index Scan
def index_scan_ann(qep, aqps):
    other_scans = ['Seq Scan', 'Bitmap Index Scan']
    scans_found = []
    scan_to_cost = {}
    index_scan_cost = qep['Total Cost']
    for plan in aqps:
        for scan in other_scans:
            print(f'Finding {scan}\n')
            scan_infos = find_node_info(scan, plan, [])
            if scan_infos is not None:
                for scan_info in scan_infos:
                    if 'Alias' in scan_info:
                        if scan_info['Alias'] == qep['Alias']:
                            scan_cost = scan_info['Total Cost']
                            multiple = round(scan_cost - index_scan_cost, 2)
                            scan_to_cost[scan] = multiple
                            scans_found.append(scan)
                            print("scans_found: " + str(scans_found))
                    else:
                        if scan_info['Index Name'] == qep['Index Name']:
                            scan_cost = scan_info['Total Cost']
                            multiple = round(scan_cost - index_scan_cost, 2) # is dividing better??
                            print(f"diff in cost for {scan_info['Node Type']} is {multiple}")
                            scan_to_cost[scan] = multiple
                            scans_found.append(scan)
                            print("scans_found: " + str(scans_found))
    print("scans found list is " + str(len(scans_found)))
    
    if len(scans_found) > 0:
        ann = f"""The Index Scan operation is performed here because there is an index {qep['Index Name']} on the table {qep['Relation Name']} and an index scan has lower cost compared to a """
        s = 1
        for scan in scan_to_cost:
            ann = ann + scan + " operation which is " + str(scan_to_cost[scan]) + " more costly"
            s+=1
            if s == len(scans_found):
                ann = ann + " and a "
        return ann + '\n'
    
    # default annotation if no other scans used in aqps
    return f"""The Index Scan operation is performed here because there is an index {qep['Index Name']} on the table {qep['Alias']}.\n"""

# Index-Only Scan
def index_only_scan_ann(plan):
    return f"""The Index-Only Scan operation is performed here because only one attribute, {plan['Output']}, is needed to satisfy the query."""

# Bitmap Scan (assuming mapped to bitmap heap scan)
def bitmap_scan_ann(plan):
    filter = plan['Filter']
    filterr = format(filter)
    node_info = find_node_info('Bitmap Index Scan', plan, [])
    cond = node_info[0]['Index Cond']
    condd = format(cond)
    num_of_rows = plan['Actual Rows']
    return f"""The Bitmap Scan operation is performed here because the number of records accessed ({num_of_rows}) are too many for an index scan and too little for a sequential scan. The scan uses {filterr} and {condd} to filter the table."""


# JOIN OPERATORS

# Nested Loop Join
def nl_join_ann(qep):
    row1 = 0
    row2 = 0
    for child in qep['Plans']:
        # print(child['Node Type'])
        if row1 == 0:
            row1 = child['Actual Rows']
        else:
            row2 = child['Actual Rows']
    # print(f"{row1} and {row2}")
    return f"""The Nested Loop Join operation is performed here because one of the child node's output is significantly smaller than the other. In this case, one has {row1} rows and the other has {row2} rows.\n"""

# Nested Loop Semi Join
def nl_semi_join_ann():
    return f"""The Nested Loop Semi Join operation is performed here because there is an EXISTS clause in the query that requires the outer rows to be filtered by the inner rows, returning the results of the outer rows only.\n"""

# Merge Join
def merge_join_ann(qep, aqps):
    cond = qep['Merge Cond']
    condd = format(cond)

    # Finding number of rows on each side of the join
    row1 = 0
    row2 = 0
    for child in qep['Plans']:
        if row1 == 0:
            row1 = child['Actual Rows']
        else:
            row2 = child['Actual Rows']
    
    # Calculating cost differences in joins
    merge_join_cost = qep['Total Cost']
    join_to_cost = {}
    for plan in aqps:
        # print("\n ok new plan")
        join_infos = find_node_info('Hash Join', plan, [])
        for join_info in join_infos:
            if join_info['Hash Cond'] == cond:
                join_cost = join_info['Total Cost']
                diff = round(join_cost - merge_join_cost, 2)
                join_to_cost[join_info['Node Type']] = diff
    return f"""The Merge Join operation is performed here because both tables are sorted and the join clause is '=' as in {condd}. Both sides of the join are also large at {row1} and {row2} rows. Merge join is {join_to_cost['Hash Join']} less costly than a hash join.\n"""

# Hash Join
def hash_join_ann(qep, aqps):
    cond = qep['Hash Cond']
    condd = format(cond)

    # Find number of rows on each side of the join
    row1 = 0
    row2 = 0
    for child in qep['Plans']:
        if row1 == 0:
            row1 = child['Actual Rows']
        else:
            row2 = child['Actual Rows']
    
    # Compare costs with Nested Loop and Merge Join (if any)
    other_joins = ['Nested Loop', 'Merge Join']
    joins_found = []
    join_to_cost = {}
    hash_join_cost = qep['Total Cost']
    for plan in aqps:
        for join in other_joins:
            print(f'\nFinding {join}')
            join_infos = find_node_info(join, plan, [])
            if join_infos is not None:
                for join_info in join_infos:
                    if join_info['Output'] == qep['Output']:
                        join_cost = join_info['Total Cost']
                        diff = round(join_cost - hash_join_cost, 2)
                        join_to_cost[join] = diff
                        joins_found.append(join)
                        # print("scans_found: " + str(joins_found))
    print("joins found list is " + str(len(joins_found)))
    if len(joins_found) > 0:
        ann = f"""The Hash Join operation is performed here because the join clause is '=' as in {condd} and both sides of the join is large at {row1} and {row2} rows. The hashed table is small enough to fit the working memory (work_mem). """
        for join in join_to_cost:
            ann = ann + f"{join} is more costly by {join_to_cost[join]}. "
        return ann + '\n'
    
    # default annotation if no other joins found
    return f"""The Hash Join operation is performed here because the join clause is '=' as in {condd} and both sides of the join is large at {row1} and {row2} rows. The hashed table is small enough to fit the working memory (work_mem).\n"""

# MISC OPERATORS

# Hash
def hash_ann(plan):
    node_info = find_node_info('Index Scan', plan, [])
    table = node_info[0]['Alias']
    return f"""The Hash operation is performed here because the table '{table}' is the smaller table so minimal memory is required to store the hash table in memory. Here, the hash is done on the {plan['Output']}."""

# Sort
def sort_ann(plan):
    return f"""The Sort operation is performed here to sort according to {plan['Sort Key']}. The sorting is done by {plan['Sort Method']}."""

# Incremental Sort
def incremental_sort_ann():
    return f"""The Incremental Sort operation is performed here because it has a much lower cost due to the reduction in memory usage and the reduced likelihood of spilling the sorts into disk."""

# Aggregate
def aggregate_ann(plan):
    if 'Filter' in plan:
        filter = plan['Filter']
    else:
        for element in plan['Output']:
            funcs = ['sum', 'count', 'avg', 'max', 'min']
            for f in funcs:
                if f in element:
                    filter = element
                    print(filter)
                    break # only takes last filter because dk which is used by operator
    filterr = format(filter)
    
    if 'sum' in filter:
        return f"""The Aggregate operation is performed here because there is an aggregate function SUM in this query: {filterr}.\n"""
    elif 'count' in filter:
        return f"""The Aggregate operation is performed here because there is an aggregate function COUNT in this query: {filterr}.\n"""
    elif 'avg' in filter:
        return f"""The Aggregate operation is performed here because there is an aggregate function AVG in this query: {filterr}.\n"""
    elif 'max' in filter:
        return f"""The Aggregate operation is performed here because there is an aggregate function MAX in this query: {filterr}.\n"""
    elif 'min' in filter:
        return f"""The Aggregate operation is performed here because there is an aggregate function MIN in this query: {filterr}.\n"""
    
    # default annotation if no agg function found
    return f"""The Aggregate operation is performed here because there is a calculation to be carried out in this query.\n"""

# Hash Aggregate
def hash_aggregate_ann():
    return f"""The Hash Aggregate operation is performed here because there is a GROUP BY clause in the query and the tables are unsorted.\n"""

# Group Aggregate
def group_aggregate_ann():
    return f"""The Group Aggregate operation is performed here because there is a GROUP BY clause and the tables are sorted.\n"""

# Limit
def limit_ann():
    return f"""The Limit operation is performed here because there is a LIMIT/OFFSET clause in the SELECT query.\n"""

# Unique
def unique_ann():
    # TODO: iterate through aqps and find HashAggregate or GroupAggregate to compare costs
    return f"""The Unique operation is performed here because the query requires a distinct value to be take from the result and it has a lower cost than Hash Aggregate and Group Aggregate.\n"""

# Append
def append_ann():
    return f"""The Append operation is performed here because multiple results are combined into one.\n"""

# Gather (actually no idea why this is used, can remove?)
def gather_ann(plan):
    return f"""The Gather function is performed here because there are {plan['Workers Launched']} workers launched in child nodes and the data output from these workers need to be combined.\n"""

# Gather Merge
def gather_merge_ann():
    return f"""The Gather Merge operation is performed here because the data is sorted and the there is a need to combine the output of the child nodes.\n"""

# Materialize
def materialize_ann(plan):
    rows = plan['Plans'][0]['Actual Rows']
    return f"""The Materialize operation is performed here because there are only a few ({rows}) tuples in the output of the child node so it materializes its output into memory before passing to the next node.\n"""

# Memoize
def memoize_ann():
    # rows = plan['Plans'][0]['Actual Rows']
    return f"""The Memoize operation is performed here because there is enough available memory to cache the required rows that are have not been cached. It has a lower cost than Materialize because there are no I/O costs to the disk.\n"""

# referred to https://severalnines.com/blog/overview-various-auxiliary-plan-nodes-postgresql/

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

def print_list(list):
    for element in list:
        print(element)
        print()

# Find full information on the node
def find_node_info(node_type, query_plan, node_info):
    if 'Plan' in query_plan:
        print(query_plan['Plan']['Node Type'])
        print("ok finding info")
        if query_plan['Plan']['Node Type'] == node_type:
            print("found it in first node!")
            node_info.append(query_plan['Plan'])
        else:
            # print("going into next Plans")
            node_info = find_node_info(node_type, query_plan['Plan']['Plans'], node_info)
            print("plan traversed. found " + str(len(node_info)) + " node_info")
    else:
        if type(query_plan) is not dict:
            for x in query_plan:
                # print(x)
                print(x['Node Type'])
                if x['Node Type'] == node_type:
                    print(f"found it! returning {x['Node Type']}")
                    node_info.append(x)
                    # print(node_info)
                if 'Plans' not in x:
                    print("continuing to node beside")
                    continue
                else:
                    print("going into next Plans")
                    node_info = find_node_info(node_type, x['Plans'], node_info)
                    print(f"breaking for loop, goodbye {x['Node Type']}")
                    # break
        else:
            print(query_plan['Node Type'])
            if query_plan['Node Type'] == node_type:
                print(f"found it! returning {query_plan['Node Type']}")
                node_info.append(query_plan)
                # print(node_info)
            print("going into next Plans")
            node_info = find_node_info(node_type, query_plan['Plans'], node_info)
            print(f"goodbye {query_plan['Node Type']}")
    
    if len(node_info) > 0:
        print( f"node returned {node_info[len(node_info) - 1]['Node Type']}" )
        print("node_info length: " + str(len(node_info)))
    else:
        print("no node info")
    return node_info

def traverse_qep(qep, aqps):
    if 'Plan' in qep:
        x = qep['Plan']
        # print("In Plan now")
        node = x['Node Type']

        # TODO: add qep, aqps as args for functions that need it
        if node == 'Seq Scan':
            print(seq_scan_ann(qep))
        elif node == 'Index Scan':
            print(index_scan_ann(qep, aqps))
        elif node == 'Index Only Scan':
            print(index_only_scan_ann(x))
        elif node == 'Bitmap Heap Scan':
            print(bitmap_scan_ann(x))
        elif node == 'Nested Loop':
            print(nl_join_ann(x))
        elif node == 'Nested Loop Semi Join':
            print(nl_semi_join_ann(x))
        elif node == 'Merge Join':
            print(merge_join_ann(x))
        elif node == 'Hash Join':
            print(hash_join_ann(x))
        elif node == 'Hash':
            print(hash_ann(x))
        elif node == 'Sort':
            print(sort_ann(x))
        elif node == 'Incremental Sort':
            print(incremental_sort_ann(x))
        elif node == 'Aggregate':
            print(aggregate_ann(x))
        elif node == 'HashAggregate':
            print(hash_aggregate_ann(x))
        elif node == 'GroupAggregate':
            print(group_aggregate_ann(x))
        elif node == 'Limit':
            print(limit_ann(x))
        elif node == 'Unique':
            print(unique_ann(x))
        elif node == 'Append':
            print(append_ann(x))
        elif node == 'Gather':
            print(gather_ann(x))
        elif node == 'Gather Merge':
            print(gather_merge_ann(x))
        elif node == 'Materialize':
            print(materialize_ann(x))
        elif node == 'Memoize':
            print(memoize_ann(x))
        
        traverse_qep(x['Plans'], aqps)
    
    a = 1
    for x in qep:
        # print("In Plans " + str(a))
        if 'Node Type' in x:
            node = x['Node Type']
        else:
            return
        if node == 'Seq Scan':
            print(seq_scan_ann(x))
        elif node == 'Index Scan':
            print(index_scan_ann(x))
        elif node == 'Index Only Scan':
            print(index_only_scan_ann(x))
        elif node == 'Bitmap Heap Scan':
            print(bitmap_scan_ann(x))
        elif node == 'Nested Loop':
            print(nl_join_ann(x))
        elif node == 'Nested Loop Semi Join':
            print(nl_semi_join_ann(x))
        elif node == 'Merge Join':
            print(merge_join_ann(x))
        elif node == 'Hash Join':
            print(hash_join_ann(qep, aqps))
        elif node == 'Hash':
            print(hash_ann(x))
        elif node == 'Sort':
            print(sort_ann(x))
        elif node == 'Incremental Sort':
            print(incremental_sort_ann(x))
        elif node == 'Aggregate':
            print(aggregate_ann(x))
        elif node == 'HashAggregate':
            print(hash_aggregate_ann(x))
        elif node == 'GroupAggregate':
            print(group_aggregate_ann(x))
        elif node == 'Limit':
            print(limit_ann(x))
        elif node == 'Unique':
            print(unique_ann(x))
        elif node == 'Append':
            print(append_ann(x))
        elif node == 'Gather':
            print(gather_ann(x))
        elif node == 'Gather Merge':
            print(gather_merge_ann(x))
        elif node == 'Materialize':
            print(materialize_ann(x))
        elif node == 'Memoize':
            print(memoize_ann(x))

        if 'Plans' in x:
            traverse_qep(x['Plans'], aqps)
        else:
            continue
        a+=1
    return

# Annotates the sql query. Argument is a list of query plans, 1st being QEP and the rest are AQPs
def annotate(plans):
    num_of_aqp = len(plans) - 1
    qep = plans[0]
    aqps = plans[1:]

    traverse_qep(qep, aqps)

# conn = connect()
# cur = conn.cursor()

# filename = 'GUI\Queries\q6.sql'

# fd = open(filename, 'r')
# sqlquery = fd.read()
# fd.close()

# node_types_d = {}
# query_plans = []

# # Getting query plan
# cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + sqlquery)
# plan = cur.fetchall()
# # print(plan)
# # node_types = process_QEP(plan, query_plans, node_types_d)[0]
# print()

# Getting QEP + AQPs
with open('query_plans'+'9'+'.pkl', 'rb') as f:
    all_plans = pickle.load(f)

# Getting the list of annotations corresponding to the nodes
# ann_list = obtain_ann_list(plan)
# print_list(ann_list)
# annotate(all_plans)
qep = all_plans[0]
aqps = all_plans[1:]
a = find_node_info('Aggregate', qep, [])
print()
# print(a[0])
print()
print(aggregate_ann(a[0]))



# fetch_AQPS(cur, node_types.keys(), sqlquery, query_plans)
# print("\nTotal number of query plans: " + str(len(query_plans)))


# cur.close()
# conn.close()
# print('Database is disconnected.')