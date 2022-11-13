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
    if '::text' in string:
        string = string.replace('::text', '')
    
    return string

# SCAN OPERATORS

# Sequential Scan
def seq_scan_ann(plan):
    if 'Filter' in plan:
        cond = plan['Filter']
        condd = format(cond)
        return f"""The Sequential Scan operation is performed here because there is no index created on the table '{plan['Alias']}', hence the only way is to go through the table tuple by tuple. Tuples that do not satisfy {condd} are removed from the output.\n"""
    return f"""The Sequential Scan operation is performed here because there is no index created on the table '{plan['Alias']}', hence the only way is to go through the table tuple by tuple.\n"""


# Index Scan
def index_scan_ann(qep, aqps):
    index_scan_cost = qep['Total Cost']
    scan_to_cost = compare_costs(qep, index_scan_cost, aqps)
    
    if len(scan_to_cost) > 0:
        ann = f"""The Index Scan operation is performed here because there is an index {qep['Index Name']} on the table {qep['Relation Name']} and an index scan has lower cost compared to a """
        s = 1
        for scan in scan_to_cost:
            ann = ann + scan + " operation which is " + str(scan_to_cost[scan]) + " more costly"
            s+=1
            if s == len(scan_to_cost):
                ann = ann + " and a "
        return ann + '\n'
    
    # default annotation if no other scans used in aqps
    return f"""The Index Scan operation is performed here because there is an index {qep['Index Name']} on the table {qep['Alias']}.\n"""


# Index-Only Scan
def index_only_scan_ann(plan):
    return f"""The Index-Only Scan operation is performed here because only one attribute, {plan['Output']}, is needed to satisfy the query.\n"""


# Bitmap Scan
def bitmap_scan_ann(plan):
    filter = plan['Filter']
    filterr = format(filter)
    node_info = find_node_info('Bitmap Index Scan', plan, [])
    cond = node_info[0]['Index Cond']
    condd = format(cond)
    num_of_rows = plan['Actual Rows']
    return f"""The Bitmap Scan operation is performed here because the number of records accessed ({num_of_rows}) are too many for an index scan and too little for a sequential scan. The scan uses {filterr} and {condd} to filter the table.\n"""


# JOIN OPERATORS

# Nested Loop Join
def nl_join_ann(plan):
    row1 = 0
    row2 = 0
    for child in plan['Plans']:
        # print(child['Node Type'])
        if row1 == 0:
            row1 = child['Actual Rows']
        else:
            row2 = child['Actual Rows']
    # print(f"{row1} and {row2}")
    return f"""The Nested Loop Join operation is performed here because one of the child node's output is significantly smaller than the other. In this case, one has {row1} rows and the other has {row2} rows.\n"""


# Nested Loop Semi Join
def nl_semi_join_ann(plan):
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
    join_to_cost = compare_costs(qep, merge_join_cost, aqps)
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
    hash_join_cost = qep['Total Cost']
    join_to_cost = compare_costs(qep, hash_join_cost, aqps)
    if len(join_to_cost) > 0:
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
    if node_info:
        table = node_info['Alias']
        return f"""The Hash operation is performed here because the table '{table}' is the smaller table so minimal memory is required to store the hash table in memory. Here, the hash is done on the {plan['Output']}\n."""
    return f"""The Hash operation is performed here because the table is the smaller table so minimal memory is required to store the hash table in memory. Here, the hash is done on the {plan['Output']}\n."""


# Sort
def sort_ann(plan):
    return f"""The Sort operation is performed here to sort according to {plan['Sort Key']}. The sorting is done by {plan['Sort Method']}.\n"""


# Incremental Sort
def incremental_sort_ann():
    return f"""The Incremental Sort operation is performed here because it has a much lower cost due to the reduction in memory usage and the likelihood of spilling the sorts into disk.\n"""


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
    return f"""The Limit operation is performed here because there is a LIMIT/OFFSET clause in the SELECT query. \n"""


# Unique
def unique_ann():
    return f"""The Unique operation is performed here because the query requires a distinct value to be take from the result.\n"""


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


def print_list(list):
    for element in list:
        print(element)
        print()

def compare_costs(qep, cost, aqps):
    if qep['Node Type'] == 'Index Scan':
        other_scans = ['Seq Scan', 'Bitmap Index Scan']
        scans_found = []
        scan_to_cost = {}
        for plan in aqps:
            for scan in other_scans:
                print(f'Finding {scan}\n')
                scan_infos = find_node_info(scan, plan, [])
                if scan_infos is not None:
                    for scan_info in scan_infos:
                        if 'Alias' in scan_info:
                            if scan_info['Alias'] == qep['Alias']:
                                scan_cost = scan_info['Total Cost']
                                diff = round(scan_cost - cost, 2)
                                scan_to_cost[scan] = diff
                                scans_found.append(scan)
                                # print("scans_found: " + str(scans_found))
                        else:
                            if scan_info['Index Name'] == qep['Index Name']:
                                scan_cost = scan_info['Total Cost']
                                diff = round(scan_cost - cost, 2) # is dividing better??
                                print(f"diff in cost for {scan_info['Node Type']} is {diff}")
                                scan_to_cost[scan] = diff
                                scans_found.append(scan)
                                # print("scans_found: " + str(scans_found))
        return scan_to_cost
    elif qep['Node Type'] == 'Merge Join':
        join_to_cost = {}
        for plan in aqps:
            join_infos = find_node_info('Hash Join', plan, [])
            for join_info in join_infos:
                if join_info['Hash Cond'] == qep['Merge Cond']:
                    join_cost = join_info['Total Cost']
                    diff = round(join_cost - cost, 2)
                    join_to_cost[join_info['Node Type']] = diff
        return join_to_cost
    else:
        other_joins = ['Nested Loop', 'Merge Join']
        joins_found = []
        join_to_cost = {}
        for plan in aqps:
            for join in other_joins:
                print(f'\nFinding {join}')
                join_infos = find_node_info(join, plan, [])
                if join_infos is not None:
                    for join_info in join_infos:
                        if join_info['Output'] == qep['Output']:
                            join_cost = join_info['Total Cost']
                            diff = round(join_cost - cost, 2)
                            join_to_cost[join] = diff
                            joins_found.append(join)
                            # print("scans_found: " + str(joins_found))
        return join_to_cost

# Compare overall costs of plans
def compare_plans(plans):
    plans_dict = {}
    plans_dict['qep'] = plans[0]['Plan']['Total Cost']
    x = 1
    for plan in plans[1:]:
        key = 'aqp ' + str(x)
        plans_dict[key] = plan['Plan']['Total Cost']
        x+=1
    compare_ann = ""
    for key in plans_dict:
        compare_ann+= f"\n{key} costs {plans_dict[key]}."
    return compare_ann

# Find full information on the node
def find_node_info(node_type, query_plan, node_info):
    if 'Plan' in query_plan:
        if query_plan['Plan']['Node Type'] == node_type:
            node_info.append(query_plan['Plan'])
        else:
            node_info = find_node_info(node_type, query_plan['Plan']['Plans'], node_info)
            print("plan traversed. found " + str(len(node_info)) + " node_info")
    else:
        if type(query_plan) is not dict:
            for x in query_plan:
                if x['Node Type'] == node_type:
                    node_info.append(x)
                if 'Plans' not in x:
                    continue
                else:
                    node_info = find_node_info(node_type, x['Plans'], node_info)
        else:
            if query_plan['Node Type'] == node_type:
                node_info.append(query_plan)
            node_info = find_node_info(node_type, query_plan['Plans'], node_info)
            
    return node_info

def compare_plans(plans):
    plans_dict = {}
    plans_dict['qep'] = plans[0]['Plan']['Total Cost']
    x = 1
    for plan in plans[1:]:
        key = 'aqp ' + str(x)
        plans_dict[key] = plan['Plan']['Total Cost']
        x+=1
    compare_ann = ""
    for key in plans_dict:
        compare_ann+= f"\n{key} costs {plans_dict[key]}."
    return compare_ann


# Annotates according to the nodes found in the qep
def traverse_qep(qep, aqps, string_v):
    print("inside traverse")
    print(string_v)


    if 'Plan' in qep:
        x = qep['Plan']
        node = x['Node Type']

        if node == 'Seq Scan':
            string_v += (seq_scan_ann(x))
        elif node == 'Index Scan':
            string_v +=(index_scan_ann(x, aqps))
        elif node == 'Index Only Scan':
            string_v +=(index_only_scan_ann(x))
        elif node == 'Bitmap Heap Scan':
            string_v +=(bitmap_scan_ann(x))
        elif node == 'Nested Loop':
            string_v +=(nl_join_ann(x))
        elif node == 'Nested Loop Semi Join':
            string_v +=(nl_semi_join_ann())
        elif node == 'Merge Join':
            string_v +=(merge_join_ann(x, aqps))
        elif node == 'Hash Join':
            string_v +=(hash_join_ann(x, aqps))
        elif node == 'Hash':
            string_v +=(hash_ann(x))
        elif node == 'Sort':
            string_v +=(sort_ann(x))
        elif node == 'Incremental Sort':
            string_v +=(incremental_sort_ann())
        elif node == 'Aggregate':
            string_v +=(aggregate_ann(x))
        elif node == 'HashAggregate':
            string_v +=(hash_aggregate_ann())
        elif node == 'GroupAggregate':
            string_v +=(group_aggregate_ann())
        elif node == 'Limit':
            string_v +=(limit_ann())
        elif node == 'Unique':
            string_v +=(unique_ann())
        elif node == 'Append':
            string_v +=(append_ann())
        elif node == 'Gather':
            string_v +=(gather_ann(x))
        elif node == 'Gather Merge':
            string_v +=(gather_merge_ann())
        elif node == 'Materialize':
            string_v +=(materialize_ann(x))
        elif node == 'Memoize':
            string_v +=(memoize_ann())

        if 'Plans' not in qep['Plan']:
            return string_v
        else:
            string_v = traverse_qep(x['Plans'], aqps, string_v)

    # a = 1
    for x in qep:
        # print("In Plans " + str(a))
        if 'Node Type' in x:
            node = x['Node Type']
        else:
            return string_v

        if node == 'Seq Scan':
            string_v +=(seq_scan_ann(x))
        elif node == 'Index Scan':
            string_v +=(index_scan_ann(x, aqps))
        elif node == 'Index Only Scan':
            string_v +=(index_only_scan_ann(x))
        elif node == 'Bitmap Heap Scan':
            string_v +=(bitmap_scan_ann(x))
        elif node == 'Nested Loop':
            string_v +=(nl_join_ann(x))
        elif node == 'Nested Loop Semi Join':
            string_v +=(nl_semi_join_ann())
        elif node == 'Merge Join':
            string_v +=(merge_join_ann(x, aqps))
        elif node == 'Hash Join':
            string_v +=(hash_join_ann(x, aqps))
        elif node == 'Hash':
            string_v +=(hash_ann(x))
        elif node == 'Sort':
            string_v +=(sort_ann(x))
        elif node == 'Incremental Sort':
            string_v +=(incremental_sort_ann())
        elif node == 'Aggregate':
            string_v +=(aggregate_ann(x))
        elif node == 'HashAggregate':
            string_v +=(hash_aggregate_ann())
        elif node == 'GroupAggregate':
            string_v +=(group_aggregate_ann())
        elif node == 'Limit':
            string_v +=(limit_ann())
        elif node == 'Unique':
            string_v +=(unique_ann())
        elif node == 'Append':
            string_v +=(append_ann())
        elif node == 'Gather':
            string_v +=(gather_ann(x))
        elif node == 'Gather Merge':
            string_v +=(gather_merge_ann())
        elif node == 'Materialize':
            string_v +=(materialize_ann(x))
        elif node == 'Memoize':
            string_v +=(memoize_ann())

        if 'Plans' in x:
            string_v = traverse_qep(x['Plans'], aqps, string_v)
        else:
            continue
        # a += 1

    # print("|||||||||||||||||||||||")
    # print(string_v)

    return string_v

def generate_table(mapping):
    #This gets all the query terms of a query 'i'
    # qtlist = i.return_query_terms_list()
    # nodelinelist = i.return_node_line()
    # print("SIZE OF QUERY TERMS LIST: " + str(len(qtlist)))
    #print(tabulate(qtlist, tablefmt="grid"))

    head = ['Line No.', 'Query Terms', 'QEP']
    AEP_counter = len(mapping)
    for i in range(AEP_counter):
        head.append('AEP' + str(i+1))
    
    qtlist = mapping[0].return_query_terms_list()
    nodelinelist = mapping[0].return_node_line()

    cols = (len(mapping)) + 2
    table = [["" for i in range(cols)] for j in range(len(qtlist))]
    
    count = 0
    for j in qtlist:
        table[count][0] = nodelinelist[count][0] #line number
        table[count][1] = j #query term
        count+=1
    
    for i in range(2,2+len(mapping),1):
        nodelinelist = mapping[i-2].return_node_line()

        count = 0
        for j in qtlist:
            table[count][i] = nodelinelist[count][1]
            count+=1
    
    print(tabulate(table, headers=head, tablefmt="grid"))

    return table

    







    # for i in mapping:
    #     # print()
    #     # i.print_sql_query_list()

    #     #This gets all the query terms of a query in a list
    #     #qtlist = i.return_query_terms_list()
    #     nodelinelist = i.return_node_line()
    #     print("SIZE OF QUERY TERMS LIST: " + str(len(qtlist)))
    #     #print(tabulate(qtlist, tablefmt="grid"))
        
        


    #     cols = (len(mapping)) + 1

    #     table = [["" for i in range(cols)] for j in range(len(qtlist))]
    #     count = 0
    #     for j in qtlist:
    #         for k in range(cols):
    #             table[count][k] = nodelinelist[count][0] #line number
    #             table[count][k] = j #query term
    #         count+=1

    
