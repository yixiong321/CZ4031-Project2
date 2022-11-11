# TODO: map sql query to plans

import sqlparse
#!/usr/bin/python
import psycopg2
import json
from pathlib import Path
import re

q2 = '''select
	o_orderpriority,
	count(*) as order_count
from
	orders
where
	o_orderdate >= date '1996-03-01'
	and exists 
        (select
			*
		from
			lineitem
		where
			l_orderkey = o_orderkey 
			and l_commitdate < l_receiptdate
	)
group by
	o_orderpriority
order by
	o_orderpriority
limit 1;'''

q3='''select
	l_orderkey,
	sum(l_extendedprice * (1 - l_discount)) as revenue,
	o_orderdate,
	o_shippriority
from
	customer,
	orders,
	lineitem
where
	c_mktsegment = 'BUILDING'
	and c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and o_totalprice < 50000
	and l_extendedprice > 1200
group by
	l_orderkey,
	o_orderdate,
	o_shippriority
order by
	revenue desc,
	o_orderdate'''

# create a dictionary for mapping? key would be token and value would be node details
relation_dict={}
def get_mapping(relation_dict,tokens,nodes):
    # from "tablename"
    for token in tokens:
        for node in nodes:
            for val in node.values():
                if token == val: 
                    relation_dict[token]=node
                elif token in val:
                    relation_dict[token]=node
    return relation_dict

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

# use each node's condition to map to each specific lines 
# NOTE condition might not be unqiue

def map_node_to_line(nodes,sql_query_list):
    # Scans
    search_terms=['Alias']
    print(len(nodes))
    for s in search_terms:
        for node in nodes:
            if s in node.keys():
                for line in sql_query_list:
                    temp = line.query_term+'_'+str(line.subquery_number)
                    if node[s] == line.query_term or node[s]==temp:
                        line.set_node(node)
                        if node in nodes:
                            nodes.remove(node)
    print(len(nodes))          
    # Joins & Filter
    search_terms=['Hash Cond',"Merge Cond",'index Cond'+'Filter','Join Filter']
    for s in search_terms:
        for node in nodes:
            if s in node.keys():
                for line in sql_query_list:
                    if node[s] == line.query_term:
                        line.set_node(node)

def node_to_lines(nodes,sql_query_list):
    for node in nodes:
        values=node.values()
        for line in sql_query_list:
            if line.query_term in values:
                node['lines'].append(line.line_number)
    
    for i in nodes:
        print(i)
    #return nodes


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


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host="localhost",
            database="TPC-H",
            user="postgres",
            password="1234")
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        print()
        '''
        uncomment and tab lines below except close() for testing all queries
        may want to comment out print(x) for cleaner output
        '''
        '''
        for i in range(1,11):
            print('Query',i)
            query = Path('Queries/q' + str(i) + '.sql').read_text()
        '''
        query = Path('GUI/Queries&Json/q2.sql').read_text()
        q = Query(query)
        cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + q.get_query())
        rows = cur.fetchall()
        x = json.dumps(rows)
        #print(x)
        print()
        nodes=[]
        for a in rows[0][0]:
            display(a['Plan'],nodes)
        print()
        print('Nodes:')
        print(nodes)
        q.process_query()
        
        #map_node_to_line(nodes,q.sql_query_list)
        node_to_lines(nodes,q.sql_query_list)
        q.print_sql_query_list()
        
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def display(plan,nodes,level=0):
    print('    ' * level, end='')
    node={'lines':[]}
    print(plan['Node Type'] + '|', end='')
    node['Node Type'] = plan['Node Type']
    if 'Join Type' in plan:# Loop/Join
        print(plan['Join Type'] + ' ', end='')
        node["Join Type"] = plan['Join Type']
        if 'Join Filter' in plan:
            node['Join Filter']=plan['Join Filter']    
        #node['Joining']= [plan['Plans'][0]['Node Type'],plan['Plans'][1]['Node Type']]
        #node["Cond"]=process_cond(plan['Plans'][1]['Index Cond']) # 1 is the inner loop
    
    explore(plan) # trying to find interesting keys

    # args specific to type
    # Sort

    if 'Sort Method' in plan:
        print('(' + plan['Sort Method'] + ')', end='')
        node['Sort Method']=plan['Sort Method']
        node['Sort Key']=plan['Sort Key']
    # Seq scan
    if 'Relation Name' in plan:
        print('table:' + plan['Relation Name'] + ' ', end='')
        
        node['Relation Name']=plan['Relation Name']
    # Aggregate
    if 'Strategy' in plan:
        print('(' + plan['Strategy'] + ') ', end='')
        node['Strategy'] = plan['Strategy']
    if 'Group Key' in plan:
        print('GROUP BY ' + str(plan['Group Key']) + ' ', end='')
        node['Group Key']= plan['Group Key']
    if 'Subplan Name' in plan:
        print('AS ' + plan['Subplan Name'] + ' ', end='')
        node['Subplan Name']=plan['Subplan Name']
    # Seq scan & aggregate
    if 'Filter' in plan:
        print('filter:' + convert_condition(plan['Filter']) + ' ', end='')
        node['Filter']= convert_condition(plan['Filter'])
    # Hash join
    if 'Hash Cond' in plan:
        print('cond:' + convert_condition(plan['Hash Cond']) + ' ', end='')
        node['Hash Cond']=convert_condition(plan['Hash Cond'])
    # Merge join
    if 'Merge Cond' in plan:
        print('cond:' + convert_condition(plan['Merge Cond']) + ' ', end='')
        node['Merge Cond']=convert_condition(plan['Merge Cond'])
    # Index only scan # this cond most prob used for NL join
    if 'Index Cond' in plan:
        print('cond:' + convert_condition(plan['Index Cond']) + ' ', end='')
        node['Index Cond']=convert_condition(plan['Index Cond'])
    if 'Alias' in plan:
        print("AS " + plan['Alias'], end='')
        node['Alias']=plan['Alias']
    print()
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
    

connect()

# problems:
# 1) unable to map nested loop node -- outer and inner ? no condition!!
# 2) nested queries



# use sql parse to format the sql query to a uniform format
# split and assign an line index to the string

# one key can map to more than 1 node 
# for each key , store the node and line indexes

# 
# like lineitem.l_commitdate < lineitem.l_receiptdate convert to
#  l_commitdate < l_receiptdate 

# # (a.b = c.d) -> b = c 
# raw = re.sub(r'\((\w+\.)?(\w+) = (\w+\.)?(\w+)\)', r'\2 = \4', raw) 
# (a = 'b'::type) -> a = 'b' 
# raw = re.sub(r"\((\w+) = ('\w+')(::\w+)\)", r'\1 = \2', raw) 

# custom class of key,index,node

# custom class
class relation():
    def __init__(self,keyterm,line_number,level,node):
        self.line_number=line_number
        self.keyterm = keyterm
        self.node=node 
        self.level = level



            




