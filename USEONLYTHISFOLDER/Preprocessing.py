# https://www.postgresql.org/docs/9.2/runtime-config-query.html#RUNTIME-CONFIG-QUERY-CONSTANTS
import psycopg2
import queue
import sqlparse
import re

def execute_originalquery(cursor, query):
    # Executing an MYSQL function using the execute() method
    # Setting configurations that we did not learn before off.
    cursor.execute(
        "Set enable_hashagg = off; Set enable_material= off; Set enable_indexonlyscan = off ; Set enable_tidscan = off;")
    cursor.execute("EXPLAIN (FORMAT JSON, ANALYZE) " + query)
    # Fetch a single row using fetchone() method.
    result = cursor.fetchall()
    # print("Results: ", result)
    return result


# Iterate and compare plans, return True if same , false if different
def compare_plans(original_plan, alternate_plan):
    original_plan = original_plan[0][0][0]["Plan"]
    alternate_plan = alternate_plan[0][0][0]["Plan"]
    # if not
    q1 = queue.Queue()
    q2 = queue.Queue()
    q1.put(original_plan)
    q2.put(alternate_plan)

    while not q1.empty():
        current_plan = q1.get()
        alt_plan = q2.get()
        node_type1 = current_plan["Node Type"]
        node_type2 = alt_plan["Node Type"]
        if (node_type1 == node_type2):
            if "Plans" in current_plan and "Plans" in alt_plan:
                for element in current_plan["Plans"]:
                    # print(element["Node Type"])
                    q1.put(element)
                for element in alt_plan["Plans"]:
                    # print(element["Node Type"])
                    q2.put(element)
                # q1.put(current_plan["Plans"][0])
                # q2.put(alt_plan["Plans"][0])
        else:
            return False
    return True


def check_for_join(original_plan):
    original_plan = original_plan[0][0][0]["Plan"]
    q1 = queue.Queue()
    q1.put(original_plan)
    while not q1.empty():
        current_plan = q1.get()
        if current_plan.get('Plan') is not None:
            if "Join" in current_plan["Node Type"]:
                return True
            else:
                for element in current_plan["Plans"]:
                    q1.put(element)

    return False


def iterating_alternate_config_list(plans_list, original_plan, cursor, query, conn, off_config, on_config, have_join):
    # Alternate plans (Max: 10)
    # Checking for AEP for Joins
    if have_join:
        # Full Merge Join
        plan = execute_alternatequery(conn, cursor, query, off_config, on_config, ["Nested Loop", "Hash Join"])
        if (plan != "error"):
            skip = False
            for element in plans_list:
                if compare_plans(element, plan):
                    skip = True
                    break
            if not skip:
                print("plan added")
                plans_list.append(plan)

        # Full hash join
        plan = execute_alternatequery(conn, cursor, query, off_config, on_config, ['Nested Loop', "Merge Join"])
        if (plan != "error"):
            skip = False
            for element in plans_list:
                if compare_plans(element, plan):
                    skip = True
                    break
            if not skip:
                print("plan added")
                plans_list.append(plan)

        # Full nested loop join
        plan = execute_alternatequery(conn, cursor, query, off_config, on_config, ['Merge Join', "Hash Join"])
        if (plan != "error"):
            skip = False
            for element in plans_list:
                if compare_plans(element, plan):
                    skip = True
                    break
            if not skip:
                print("plan added")
                plans_list.append(plan)

    # Checking for AEP for Scans
    # Seq scan
    plan = execute_alternatequery(conn, cursor, query, off_config, on_config,
                                  ["Index Scan", "Bitmap Scan"])
    if (plan != "error"):
        skip = False
        for element in plans_list:
            if compare_plans(element, plan):
                skip = True
                break
        if not skip:
            print("plan added")
            plans_list.append(plan)

    # Index Scan
    plan = execute_alternatequery(conn, cursor, query, off_config, on_config,
                                  ["Seq Scan", "Bitmap Scan"])
    if (plan != "error"):
        skip = False
        for element in plans_list:
            if compare_plans(element, plan):
                skip = True
                break
        if not skip:
            print("plan added")
            plans_list.append(plan)

    # Bitmap Scan
    plan = execute_alternatequery(conn, cursor, query, off_config, on_config,
                                  ["Seq Scan", "Index Scan"])  # "Index Only Scan", "Tid Scan"
    if (plan != "error"):
        skip = False
        for element in plans_list:
            if compare_plans(element, plan):
                skip = True
                break
        if not skip:
            print("plan added")
            plans_list.append(plan)

    ## Index Only Scan
    # plan = execute_alternatequery(conn, cursor, query, off_config, on_config,
    #                               ["Seq Scan", "Index Scan", "Bitmap Scan", "Tid Scan"])
    # if (plan != "error"):
    #     skip = False
    #     for element in plans_list:
    #         if compare_plans(element, plan):
    #             skip = True
    #             break
    #     if not skip:
    #         print("plan added")
    #         plans_list.append(plan)
    # # Tid Only Scan
    # plan = execute_alternatequery(conn, cursor, query, off_config, on_config,
    #                               ["Seq Scan", "Index Scan", "Bitmap Scan", "Index Only Scan"])
    # if (plan != "error"):
    #     skip = False
    #     for element in plans_list:
    #         if compare_plans(element, plan):
    #             skip = True
    #             break
    #     if not skip:
    #         print("plan added")
    #         plans_list.append(plan)

    # Checking for AEP for Sort
    # Sort
    plan = execute_alternatequery(conn, cursor, query, off_config, on_config, ["Sort"])
    if (plan != "error"):
        skip = False
        for element in plans_list:
            if compare_plans(element, plan):
                skip = True
                break
        if not skip:
            print("plan added")
            plans_list.append(plan)
    # Checking for AEP for Others
    # # No Hash Agg
    # plan = execute_alternatequery(conn, cursor, query, off_config, on_config, ["Hash Agg"])
    # if (plan != "error"):
    #     skip = False
    #     for element in plans_list:
    #         if compare_plans(element, plan):
    #             skip = True
    #             break
    #     if not skip:
    #         print("plan added")
    #         plans_list.append(plan)
    # # No Material
    # plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Material"])
    # if(plan != "error" and not compare_plans(original_plan,plan)):
    #       plans_list.append(plan)
    return plans_list


def execute_alternatequery(conn, cursor, query, off_config, on_config, off=[]):
    try:
        # 100s timeout
        cursor.execute("set statement_timeout = 100000")
        # Setting configurations that we did not learn before off ensure they do not appear in our AQPs.
        cursor.execute(
            "Set enable_hashagg = off; Set enable_material= off; Set enable_indexonlyscan = off ; Set enable_tidscan = off;  ")
        # Setting off for alternate query plans
        for condition in off:
            cursor.execute(off_config[condition])

        print("######### STARTING EXECUTING SQL COMMAND! MIGHT FREEZE PC! #########")

        cursor.execute(query)
        alternate_plan = cursor.fetchall()

        # Setting config back on to set up for next alternate query plan
        for condition in off:
            cursor.execute(on_config[condition])

        # print(alternate_plan)
        print("######### FINISHED EXECUTING SQL COMMAND! GOING TO NEXT! #########")

        return alternate_plan

    except(Exception, psycopg2.DatabaseError) as error:
        # Check error
        print("Your error: ", error)
        conn.rollback()
        return "error"


def generate_aqp(original_plan, cursor, query, conn, have_join):
    plans_list = []

    # if have join use full config list
    if have_join:
        off_config = {
            # Joins
            "Hash Join": "set enable_hashjoin=off",
            "Merge Join": "set enable_mergejoin=off",
            "Nested Loop": "set enable_nestloop=off",
            # Scans
            "Seq Scan": "set enable_seqscan=off",
            "Index Scan": "set enable_indexscan=off",
            "Bitmap Scan": "set enable_bitmapscan=off",
            # Sort
            "Sort": "set enable_sort=off",
        }
        on_config = {
            # Joins
            "Hash Join": "set enable_hashjoin=on",
            "Merge Join": "set enable_mergejoin=on",
            "Nested Loop": "set enable_nestloop=on",
            # Scans
            "Seq Scan": "set enable_seqscan=on",
            "Index Scan": "set enable_indexscan=on",
            "Bitmap Scan": "set enable_bitmapscan=on",
            # Sort
            "Sort": "set enable_sort=on",
        }

    # Else shrink list
    else:
        off_config = {
            # Scans
            "Seq Scan": "set enable_seqscan=off",
            "Index Scan": "set enable_indexscan=off",
            "Bitmap Scan": "set enable_bitmapscan=off",
            # Sort
            "Sort": "set enable_sort=off",
        }
        on_config = {
            # Scans
            "Seq Scan": "set enable_seqscan=on",
            "Index Scan": "set enable_indexscan=on",
            "Bitmap Scan": "set enable_bitmapscan=on",
            # Sort
            "Sort": "set enable_sort=on",
        }

    # add original plan to list
    plans_list.append(original_plan)
    # print(plans_list)
    raw_query = query
    query = "EXPLAIN (FORMAT JSON, ANALYZE) " + query
    # Iterate to off configs
    plans_list = iterating_alternate_config_list(plans_list, original_plan, cursor, query, conn, off_config, on_config,
                                                 have_join)
    plans_list = find_plan_cost(plans_list)
    mapping = get_mapping(plans_list, raw_query)
    #print(len(mapping))
    #print(mapping[0].print_sql_query_list())
    #print(mapping[len(mapping)-1].print_sql_query_list())
    return plans_list , mapping


def find_plan_cost(plans_list):
    for plan in plans_list:
        q1 = queue.Queue()
        q1.put(plan[0][0][0]["Plan"])
        plan_cost = 0
        while not q1.empty():
            current_plan = q1.get()
            plan_cost += current_plan["Total Cost"]
            if "Plans" in current_plan:
                for element in current_plan["Plans"]:
                    q1.put(element)

        # Add additional field for plan_cost
        plan[0][0][0]["Plan Cost"] = plan_cost
    return plans_list


def repackage_output(plans_list):
    new_plan_list = []
    for element in plans_list:
        new_plan_list.append(element[0][0][0])
    return new_plan_list

# if __name__ == "__main__":
# Need .env file info / take input from interface.py
# Need to take in query from interface.py
# try:
#    conn = psycopg2.connect(
#        database=config('DATABASE'), user=config('USER'), password=config('PASSWORD'), host=config('HOST'),
#        port=config('PORT')
#    )
#    print("Connected!")
# except:
#    print("Failed to connect to DB!")
# Creating a cursor object using the cursor() method


# cursor = conn.cursor()
## query = " select c_custkey, count(o_orderkey) from customer left outer join orders on c_custkey = o_custkey and o_comment not like '%pending%packages%' group by c_custkey;"
# query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from customer, orders, lineitem where c_mktsegment = 'HOUSEHOLD' and c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate < date '1995-03-21' and l_shipdate > date '1995-03-21' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10; "
# result = execute_originalquery(cursor, query)
# # if no join in QEP, shrink off and on config list
# if check_for_join(result):
#     plans_list = generate_aqp(result, cursor, query, conn, True)
# else:
#     plans_list = generate_aqp(result, cursor, query, conn, False)
# # For checking
# for element in plans_list:
#     print(element)
#     print("-----------------------------------")
# # Closing the connection
# conn.close()

def get_mapping(plans_list,query):
    mapping_list=[]
    for plan in plans_list:
        q=Query(query)
        nodes=[]
        for a in plan[0][0]:
            display(a['Plan'],nodes)
        q.process_query()
        map_node_to_line(nodes,q.sql_query_list)
        mapping_list.append(q)
    return mapping_list

def process_cond(s):
    s=s.replace('(','').replace(')','')
    s=s.split(' ')
    ans =''
    rev =''
    for j in s:
        li=j.split('.')
        if len(li)==2:
            ans=ans+li[1]
            rev=li[1]+rev
        else:
            ans=ans+' '+li[0]+' '
            rev=' '+li[0]+' '+rev
    return [ans,rev]

def map_node_to_line(nodes,sql_query_list):
    joins_cond = ['Merge Cond','Hash Cond','Join Filter']
    # settle original first?
    for term in joins_cond:
        for line in sql_query_list:
            for node in nodes:
                if term in node.keys():
                    if line.node=={}:
                        if line.query_term == node[term] or line.query_term in node[term]:
                            line.set_node(node)
                            if node in nodes:
                                nodes.remove(node)
    scans_cond = ['Alias']
    # settle original first?
    for term in scans_cond:
        for line in sql_query_list:
            for node in nodes:
                if term in node.keys():
                    if line.query_term == node[term] and line.node=={}:
                        line.set_node(node)
                        if node in nodes:
                            nodes.remove(node)

    # Index scan + cond , dont remove once added ?? or only care about scanning?
    sub = ['Relation Name','Index Cond']
    for term in sub:
        for line in sql_query_list:
            for node in nodes:
                if term in node.keys():
                    if line.node=={}:
                        if line.query_term == node[term] or line.query_term in node[term] :
                            line.set_node(node)

class line():
    def __init__(self,query_term,line_number,subquery_number):
        self.query_term=query_term
        self.line_number=line_number
        self.subquery_number=subquery_number
        self.node = {}
        
    def print_attrs(self):
        print(self.line_number,self.query_term,self.subquery_number,self.node)
    def set_node(self,node):
        self.node = node

class Query():
    def __init__(self,query):
        sqlquery = sqlparse.format(query,encoding=None,keyword_case='upper')
        self.query = sqlquery
        
    def get_query(self):
        return self.query

    def process_query(self):
        sql=self.query.replace('\t','').replace('AND ','').replace(',','').split('\n')
        for x in range(len(sql)):
            sql[x]=sql[x].lstrip()
        sql_query_list=[]
        subquery_counter=-1
        stack=[]
        j=1
        for i,query_term in enumerate(sql):
            # start of subquery
            if query_term=="SELECT" or query_term=="(SELECT":
                stack.append(query_term)
                subquery_counter+=j
                
            if query_term[0]==')':
                stack.pop()
                subquery_counter-=1
                j+=1
            sql_query_list.append(line(query_term,i,subquery_counter))
        self.sql_query_list = sql_query_list
    
    def print_sql_query_list(self):
        for i in self.sql_query_list:
            i.print_attrs()
            
def display(plan,nodes,level=0):
    #print('    ' * level, end='')
    node={}
    #print(plan['Node Type'] + '|', end='')
    node['Node Type'] = plan['Node Type']
    if 'Join Type' in plan:# Loop/Join
    #    print(plan['Join Type'] + ' ', end='')
        node["Join Type"] = plan['Join Type']
        if 'Join Filter' in plan:
            node['Join Filter']=plan['Join Filter']    
        #node['Joining']= [plan['Plans'][0]['Node Type'],plan['Plans'][1]['Node Type']]
        #node["Cond"]=process_cond(plan['Plans'][1]['Index Cond']) # 1 is the inner loop
    
    #explore(plan) # trying to find interesting keys

    # args specific to type
    # Sort

    if 'Sort Method' in plan:
    #    print('(' + plan['Sort Method'] + ')', end='')
        node['Sort Method']=plan['Sort Method']
        node['Sort Key']=plan['Sort Key']
    # Seq scan
    if 'Relation Name' in plan:
        #print('table:' + plan['Relation Name'] + ' ', end='')
        
        node['Relation Name']=plan['Relation Name']
    # Aggregate
    if 'Strategy' in plan:
    #    print('(' + plan['Strategy'] + ') ', end='')
        node['Strategy'] = plan['Strategy']
    if 'Group Key' in plan:
    #    print('GROUP BY ' + str(plan['Group Key']) + ' ', end='')
        node['Group Key']= plan['Group Key']
    if 'Subplan Name' in plan:
    #    print('AS ' + plan['Subplan Name'] + ' ', end='')
        node['Subplan Name']=plan['Subplan Name']
    # Seq scan & aggregate
    if 'Filter' in plan:
    #    print('filter:' + convert_condition(plan['Filter']) + ' ', end='')
        node['Filter']= convert_condition(plan['Filter'])
    # Hash join
    if 'Hash Cond' in plan:
    #    print('cond:' + convert_condition(plan['Hash Cond']) + ' ', end='')
        node['Hash Cond']=process_cond(plan['Hash Cond'])
    # Merge join
    if 'Merge Cond' in plan:
    #    print('cond:' + convert_condition(plan['Merge Cond']) + ' ', end='')
        node['Merge Cond']=process_cond(plan['Merge Cond'])
    # Index only scan # this cond most prob used for NL join
    if 'Index Cond' in plan:
    #    print('cond:' + convert_condition(plan['Index Cond']) + ' ', end='')
        node['Index Cond']=process_cond(plan['Index Cond'])
    if 'Alias' in plan:
    #    print("AS " + plan['Alias'], end='')
        node['Alias']=plan['Alias']
    #print()
    nodes.append(node)
    #print(nodes)
    if 'Plans' in plan:
        for p in plan['Plans']:
            display(p,nodes,level + 1)
    
            

def explore(plan):
    # trying to find interesting keys
    for key in plan.keys():
        if key not in [
        'Parent Relationship',
        'Parallel Aware',
        'Async Capable',
        'Startup Cost',
        'Total Cost',
        'Plan Rows',
        'Plan Width',
        'Actual Startup Time',
        'Actual Total Time',
        'Actual Rows',
        'Actual Loops',
        'Output',# figure out what is this and is it useful
        'Schema',
        'Rows Removed by Filter',
        'Workers',
        'Workers Planned',
        'Workers Launched',
        'Single Copy',
        'Sort Space Used',
        'Sort Space Type',
        'Partial Mode',
        'Inner Unique',
        'Sort Key', #useful?
        'Index Name',
        'Scan Direction',
        'Rows Removed by Index Recheck',
        'Cache Mode',
        'Cache Key',
        'Planned Partitions',
        'HashAgg Batches',
        'Peak Memory Usage',
        'Disk Usage',
        'Hash Buckets',
        'Original Hash Buckets',
        'Hash Batches',
        'Original Hash Batches',
        'Heap Fetches',
        'Rows Removed by Join Filter',
        'Join Filter', #useful?
        'Full-sort Groups',
        'Presorted Key',# Incremental Sort, useful?
        'Cache Hits',
        'Cache Misses',
        'Cache Evictions',
        'Cache Overflows',
        #used
        'Node Type',
        'Join Type',
        'Sort Method',
        'Relation Name',
        'Strategy',
        'Group Key',
        'Subplan Name',
        'Filter',
        'Hash Cond',
        'Merge Cond',
        'Index Cond',
        'Alias',
        'Plans'
        ]:
            print('***Interesting?:"'+ key + '" value:' + str(plan[key]), end=',')

        
def convert_condition(cond):
    #regex_list=[r'\((\w+\.)?(\w+) = (\w+\.)?(\w+)\)',r"\((\w+) = ('\w+')(::\w+)\)" ]
    # match the regex to the condition and convert before saving it in nodes
    # should be a list to store a = b , b = a 
    cond = re.sub(r'\((\w+\.)?(\w+) ([!<>=]+) (\w+\.)?(\w+)\)',r'\2 \3 \5',cond) # (a.b = c.d) -> b = c 
    cond = re.sub(r"\((\w+\.)?(\w+) ([!<>=]+) ('.+')(::\w+)\)",r"\2 \3 \4",cond) # (a = 'b'::type) -> a = 'b'

    #reverse
    cond = re.sub(r"\(('.+')(::\w+) ([!<>=]+) (\w+\.)?(\w+)\)",r"\1 \3 \5",cond) # ('a'::type = 'b') -> 'a' = b
    return cond