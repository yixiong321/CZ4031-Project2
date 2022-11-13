import sqlparse
from tabulate import tabulate


def splitQuery(query):
    sql_keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'EXISTS', 'LIMIT', 'DISTINCT']
    list1 = []
    list2 = []

    # make SQL keywords capital
    res = sqlparse.format(query, encoding=None, keyword_case="upper")

    parsed = sqlparse.parse(res)
    stmt = parsed[0]
    for i in stmt.tokens:
        list1.append(str(i))  # list1 has all the tokens generated by sqlparse

    row = 0
    for i in list1:
        # print("iteration for " + i)
        if i in sql_keywords and row == 0:
            list2.append(i)
            row += 1

        elif i not in sql_keywords:
            if 'WHERE' in i.split(None):
                row += 1
                list2.append(i)
            else:
                list2[row - 1] += i

        elif i in sql_keywords and row != 0:
            row += 1
            list2.append(i)
        # print(list2)

    return list2


# Scan Methods

# Sequential Scan
def seq_scan_ann(plan):
    # TODO: if have 'Filter', say that it is done using the filter
    return f"""The Sequential Scan operation is performed here because there is no index created on the table, hence the only way is to go through the table tuple by tuple. \n"""
    # return f"""The Sequential Scan operation is performed here because there is no index created on the table {plan['Alias']}, hence the only way is to go through the table tuple by tuple. \n"""


# Index Scan
def index_scan_ann(plan):
    # TODO: iterate through aqps to find other scans to compare costs to
    return f"""The Index Scan operation is performed here because there is an index {plan['Index Name']} on the table {plan['Alias']} and an index scan has lower cost compared to a sequential scan. \n"""


# Index-Only Scan
def index_only_scan_ann(plan):
    return f"""The Index-Only Scan operation is performed here because only one attribute, {plan['Output']}, is needed to satisfy the query. \n"""


# Bitmap Scan
def bitmap_scan_ann(plan):
    # TODO: find 'Bitmap Index Scan' to get the index cond
    # TODO: find the number of rows
    return f"""The Bitmap Scan operation is performed here because the number of records chosen are too many for the index scan and too few for the sequential scan. \n"""


# Join Methods

# Nested Loop Join
def nl_join_ann(plan):
    # TODO: iterate through aqps to find mergejoin and hashjoin
    # TODO: then compare their costs
    # TODO: find if got 'Filter', then use info in ann, if no, say joining which 2 tables (find_node_info(any scan, plan))
    return f"""The Nested Loop Join operation is performed here because the join clause is '<' OR there is no join clause. \n"""


# Nested Loop Semi Join
def nl_semi_join_ann(plan):
    return f"""The Nested Loop Semi Join operation is performed here because there is an EXISTS clause in the query that requires the outer rows to be filtered by the inner rows, returning the results of the outer rows only. \n"""


# Merge Join
def merge_join_ann(plan):
    return f"""The Merge Join operation is performed here because both tables are sorted and the join clause is '='. It has a lesser cost for the \n"""


# Hash Join
def hash_join_ann(qep):
    hash_info = find_node_info('Hash', qep)
    # TODO: iterate through aqps to find mergejoin and nestedloop
    # TODO: then compare their costs
    return f"""The Hash Join operation is performed here because a hash table has been created on .The join is done on the condition that. \n"""


# Miscellaneous Operations

# Hash
def hash_ann(plan):
    return f"""The Hash operation is performed here because the table is the smaller table so minimal memory is required to store the hash table in memory. Here, the hash is done on the {plan['Output']}. \n """


# Sort
def sort_ann(plan):
    return f"""The Sort operation is performed here to sort according to {plan['Sort Key']}. The sorting is done by {plan['Sort Method']}. \n"""


# Incremental Sort
def incremental_sort_ann(plan):
    return f"""The Incremental Sort operation is performed here because it has a much lower cost due to the reduction in memory usage and the likelihood of spilling the sorts into disk. \n"""


# Aggregate
def aggregate_ann(plan):
    if 'Filter' in plan:
        if 'sum' in plan['Filter']:
            return f"""The Aggregate operation is performed here because there is an aggregate function SUM in this query. \n"""
        elif 'count' in plan['Filter']:
            return f"""The Aggregate operation is performed here because there is an aggregate function COUNT in this query. \n"""
        elif 'avg' in plan['Filter']:
            return f"""The Aggregate operation is performed here because there is an aggregate function AVG in this query. \n"""
        elif 'max' in plan['Filter']:
            return f"""The Aggregate operation is performed here because there is an aggregate function MAX in this query. \n"""
        elif 'min' in plan['Filter']:
            return f"""The Aggregate operation is performed here because there is an aggregate function MIN in this query. \n"""
    else:
        if 'sum' in plan['Output'][0]:
            return f"""The Aggregate operation is performed here because there is an aggregate function SUM in this query. \n"""
        elif 'count' in plan['Output'][0]:
            return f"""The Aggregate operation is performed here because there is an aggregate function COUNT in this query. \n"""
        elif 'avg' in plan['Output'][0]:
            return f"""The Aggregate operation is performed here because there is an aggregate function AVG in this query. \n"""
        elif 'max' in plan['Output'][0]:
            return f"""The Aggregate operation is performed here because there is an aggregate function MAX in this query. \n"""
        elif 'min' in plan['Output'][0]:
            return f"""The Aggregate operation is performed here because there is an aggregate function MIN in this query. \n"""
    return f"""The Aggregate operation is performed here because there is a calculation to be carried out in this query. \n"""


# Hash Aggregate
def hash_aggregate_ann(plan):
    return f"""The Hash Aggregate operation is performed here because there is a GROUP BY clause in the query and the tables are unsorted. \n"""


# Group Aggregate
def group_aggregate_ann(plan):
    return f"""The Group Aggregate operation is performed here because there is a GROUP BY clause and the tables are sorted. \n"""


# Limit
def limit_ann(plan):
    return f"""The Limit operation is performed here because there is a LIMIT/OFFSET clause in the SELECT query. \n"""


# Unique
def unique_ann(plan):
    # TODO: iterate through aqps and find HashAggregate or GroupAggregate to compare costs
    return f"""The Unique operation is performed here because the query requires a distinct value to be take from the result and it has a lower cost than Hash Aggregate and Group Aggregate. \n"""


# Append
def append_ann(plan):
    return f"""The Append operation is performed here because multiple results are combined into one. \n"""


# Gather (actually no idea why this is used, can remove?)
def gather_ann(plan):
    return f"""The Gather function is performed here because there are {plan['Workers Launched']} workers launched in child nodes and the data output from these workers need to be combined. \n"""


# Gather Merge
def gather_merge_ann(plan):
    return f"""The Gather Merge operation is performed here because the data is sorted and the there is a need to combine the output of the child nodes. \n"""


# Materialize
def materialize_ann(plan):
    # TODO: find child node's number of rows
    return f"""The Materialize operation is performed here because there are only a few tuples in the output of the child node so it materializes its output into memory before passing to the next node. \n"""


# Memoize
def memoize_ann(plan):
    # TODO: find child node's number of rows
    return f"""The Memoize operation is performed here because there is enough available memory to cache the required rows that are have not been cached. It has a lower cost than Materialize because there are no I/O costs to the disk. \n"""


def print_list(list):
    for element in list:
        print(element)
        print()


# Find full information on the node
def find_node_info(node_type, query_plan):
    if 'Plan' in query_plan:
        # print(query_plan['Plan']['Node Type'])
        if query_plan['Plan']['Node Type'] == node_type:
            # print("found it in first node!")
            return query_plan['Plan']
        else:
            node_info = find_node_info(node_type, query_plan['Plan']['Plans'])
            return node_info
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

#CREATE OTHER FUNCTION FOR COMPARING THE QEP WITH AEP!
#Create separate function for comparing. Always return a string, not output in console!
#It needs to go to UI, not into console!
def traverse_qep(qep, string_v):

    if not string_v:
        string_v = ""

    if 'Plan' in qep:
        x = qep['Plan']
        node = x['Node Type']

        # TODO: add qep, aqps as args for functions that need it
        if node == 'Seq Scan':
            string_v += (seq_scan_ann(qep))
        elif node == 'Index Scan':
            string_v +=(index_scan_ann(qep))
        elif node == 'Index Only Scan':
            string_v +=(index_only_scan_ann(x))
        elif node == 'Bitmap Heap Scan':
            string_v +=(bitmap_scan_ann(x))
        elif node == 'Nested Loop':
            string_v +=(nl_join_ann(x))
        elif node == 'Nested Loop Semi Join':
            string_v +=(nl_semi_join_ann(x))
        elif node == 'Merge Join':
            string_v +=(merge_join_ann(x))
        elif node == 'Hash Join':
            string_v +=(hash_join_ann(x))
        elif node == 'Hash':
            string_v +=(hash_ann(x))
        elif node == 'Sort':
            string_v +=(sort_ann(x))
        elif node == 'Incremental Sort':
            string_v +=(incremental_sort_ann(x))
        elif node == 'Aggregate':
            string_v +=(aggregate_ann(x))
        elif node == 'HashAggregate':
            string_v +=(hash_aggregate_ann(x))
        elif node == 'GroupAggregate':
            string_v +=(group_aggregate_ann(x))
        elif node == 'Limit':
            string_v +=(limit_ann(x))
        elif node == 'Unique':
            string_v +=(unique_ann(x))
        elif node == 'Append':
            string_v +=(append_ann(x))
        elif node == 'Gather':
            string_v +=(gather_ann(x))
        elif node == 'Gather Merge':
            string_v +=(gather_merge_ann(x))
        elif node == 'Materialize':
            string_v +=(materialize_ann(x))
        elif node == 'Memoize':
            string_v +=(memoize_ann(x))

        if x['Plans']:
            string_v = traverse_qep(x['Plans'], string_v)

    a = 1
    for x in qep:
        # print("In Plans " + str(a))
        if 'Node Type' in x:
            node = x['Node Type']
        else:
            return string_v #DON'T LEAVE EMPTY RETURNS!

        if node == 'Seq Scan':
            string_v +=(seq_scan_ann(x))
        elif node == 'Index Scan':
            string_v +=(index_scan_ann(x))
        elif node == 'Index Only Scan':
            string_v +=(index_only_scan_ann(x))
        elif node == 'Bitmap Heap Scan':
            string_v +=(bitmap_scan_ann(x))
        elif node == 'Nested Loop':
            string_v +=(nl_join_ann(x))
        elif node == 'Nested Loop Semi Join':
            string_v +=(nl_semi_join_ann(x))
        elif node == 'Merge Join':
            string_v +=(merge_join_ann(x))
        elif node == 'Hash Join':
            string_v +=(hash_join_ann(qep))
        elif node == 'Hash':
            string_v +=(hash_ann(x))
        elif node == 'Sort':
            string_v +=(sort_ann(x))
        elif node == 'Incremental Sort':
            string_v +=(incremental_sort_ann(x))
        elif node == 'Aggregate':
            string_v +=(aggregate_ann(x))
        elif node == 'HashAggregate':
            string_v +=(hash_aggregate_ann(x))
        elif node == 'GroupAggregate':
            string_v +=(group_aggregate_ann(x))
        elif node == 'Limit':
            string_v +=(limit_ann(x))
        elif node == 'Unique':
            string_v +=(unique_ann(x))
        elif node == 'Append':
            string_v +=(append_ann(x))
        elif node == 'Gather':
            string_v +=(gather_ann(x))
        elif node == 'Gather Merge':
            string_v +=(gather_merge_ann(x))
        elif node == 'Materialize':
            string_v +=(materialize_ann(x))
        elif node == 'Memoize':
            string_v +=(memoize_ann(x))

        if 'Plans' in x:
            string_v = traverse_qep(x['Plans'], string_v)
        else:
            continue
        a += 1

    print("|||||||||||||||||||||||")
    print(string_v)

    return string_v

def generate_table(i):
    #This gets all the query terms of a query 'i'
    qtlist = i.return_query_terms_list()
    nodelinelist = i.return_node_line()
    print("SIZE OF QUERY TERMS LIST: " + str(len(qtlist)))
    #print(tabulate(qtlist, tablefmt="grid"))

    table = [["" for i in range(3)] for j in range(len(qtlist))]
    count = 0
    for i in qtlist:
        table[count][0] = nodelinelist[count][0] #line number
        table[count][1] = i #query term
        table[count][2] = nodelinelist[count][1] #node type
        count+=1

    return table
