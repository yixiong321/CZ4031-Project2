
#!/usr/bin/python
import psycopg2
import json
from nodetypes import node_types_dict
import sqlparse
import re

def get_unique_node_types_dic(level, dic):
    if level["Node Type"] not in dic:
        dic[level['Node Type']] = 0
    if level['Node Type'] in dic:
        dic[level['Node Type']] += 1
    if "Plans" not in level:
        return 
    else:
        for p in level['Plans']:
            get_unique_node_types_dic(p, dic)
    return dic


def get_nodelist(level, lis):
    lis.append(level['Node Type'])
    if "Plans" not in level:
        return 
    else:
        for p in level['Plans']:
            get_nodelist(p, lis)
    return lis

def convert(node,dic):
    # stopping cond, no more plans reach end of branch
    if "Plans" not in node:
        id = max(dic.keys())+1
        if 'Alias'in node:
            label = str(id)+"[label='"+node['Node Type']+"\n ("+node['Alias']+")'];\n"
        else:
            label = str(id)+"[label='"+node['Node Type']+"'];\n"
        dic[id]=label
        return dic,[str(id)+";"]
    else:
        str_list=[]
        if dic.keys():
            id = max(dic.keys())+1
        else:
            id=0
        for x in range(len(node['Plans'])):

            if 'Alias'in node:
                label = str(id)+"[label='"+node['Node Type']+"\n ("+node['Alias']+")'];\n"
            else:
                label = str(id)+"[label='"+node['Node Type']+"'];\n"
            dic[id]=label
            s=str(id)+leftArrow
            dic,rels=convert(node['Plans'][x],dic)
            for rel in rels:
                str_list.append(s+rel)
        return dic,str_list

def fetch_AQPS(cur, node_types, sqlquery, query_plans,relations_list):
        counter=1
        sqlquery = Query(sqlquery)
        for key in node_types:
            if key in node_types_dict:
                #print(node_types_dict[key])
                
                cur.execute("SET LOCAL " + node_types_dict[key] + " TO OFF")
                cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + sqlquery.get_query())
                rows = cur.fetchall()
                res = json.dumps(rows)
                res = json.loads(res)
                for x in res[0][0]:
                    if x not in query_plans.values():
                        query_plans[counter] = x
                        counter+=1
                    root = x['Plan']
                    #aqp_nodes = get_nodelist(root,new_d)
                    #print(aqp_nodes)
                    counter = 0
                    dic={}
                    dic,res = convert(root,dic)
                    label_string=''
                    for x in dic.values():
                        label_string=label_string+x
                    #print(res)
                    res.insert(0,label_string)
                    relations_list.append(res)
        return query_plans,relations_list

def fetch_QEP(cur,query, query_plans, node_types_d):
    string=''
    query=Query(query)
    cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + query.get_query())
    rows = cur.fetchall()
    res = json.dumps(rows)
    res = json.loads(res)
    for x in res[0][0]:
        query_plans['0']=x
        node_types = get_unique_node_types_dic(x['Plan'], node_types_d)
        dic = {}
        dic,res= convert(x['Plan'],dic)
        label_string=''
        for x in dic.values():
            label_string=label_string+x
        #print(dic)
        #print(res)
        res.insert(0,label_string)
    return node_types, res ,query_plans

rightArrow=" -> "
leftArrow=" <- "

def get_mapping(query_plans,query):
    mapping_list=[]
    for plan in query_plans.values():
        nodes=[]
        q=Query(query)
        display(plan['Plan'],nodes)
        q.process_query()
        map_node_to_line(nodes,q.sql_query_list)
        mapping_list.append(q)
    return mapping_list

def connect():
    """ Connect to the PostgreSQL database server """
    
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host="localhost",
            database="TPC-H",
            user="postgres",
            password="1234")
        # create a cursor
        cur = conn.cursor()
        # read test files 
        filename = 'GUI\Queries&Json\q2.sql'
        fd = open(filename, 'r')
        sqlquery = fd.read()
        fd.close()

        node_types_d = {}
        query_plans = {}
        # Formats query
        
        # Getting query plan
        block_rel=[]
        node_types,res,query_plans=fetch_QEP(cur,sqlquery,query_plans,node_types_d)
        block_rel.append(res)
        # node_types refer to the nodes in the QEP
        # res refers to the partial string input for blockdiag for QEP
        # query_plans refers to the list of query plans, currently storing only the QEP
        
        # fetching AQPS
        query_plans,block_rel = fetch_AQPS(cur,node_types.keys(),sqlquery,query_plans,block_rel)
        # query_plans stores list of plans , [QEP, 'rest of AQPs']
        # aqp_relations stores list of string input for blockdiags for AQPs
       
        mapping = get_mapping(query_plans,sqlquery)
          
        print("Total number of query plans: "+str(len(query_plans))) 
        for i in mapping:
            i.print_sql_query_list() 
       

	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


#connect()
#print(node_types_dict)

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
    # Scans # settle original first == Seq Scan
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
    def return_query_term(self):
        return self.query_term
    def return_node(self):
        #return self.node
        for key, value in self.node.items():
            if 'Node Type' in key:
                return value
            else: return "-"
    def return_lineno(self):
        return self.line_number

class Query():
    def __init__(self,query):
        sqlquery = sqlparse.format(query,encoding=None,strip_comments=True,reindent=True,keyword_case='upper')
        self.query = sqlquery
        
    def get_query(self):
        return self.query

    def process_query(self):
        
        sql=self.query.replace('SELECT','SELECT\n').replace('FROM','FROM\n').replace('WHERE','WHERE\n').replace('GROUP BY','GROUP BY\n').replace('ORDER BY',
        'ORDER BY\n').replace('\t','').replace('AND ','').replace(',','').split('\n')
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

    def return_query_terms_list(self):
        list = []
        for i in self.sql_query_list:
            list.append(i.return_query_term())
        return list

    def return_node_line(self):
        list = []
        count = 0
        for i in self.sql_query_list:  
            temp = [i.return_lineno(), i.return_node()]    
            list.append(temp)
        return list

    

def display(plan,nodes,level=0):
    #print('    ' * level, end='')
    node={}
    #print(plan['Node Type'] + '|', end='')
    node['Node Type'] = plan['Node Type']
    if 'Join Type' in plan:# Loop/Join
        #print(plan['Join Type'] + ' ', end='')
        node["Join Type"] = plan['Join Type']
        if 'Join Filter' in plan:
            node['Join Filter']=process_cond(plan['Join Filter'])    

    
    #explore(plan) # trying to find interesting keys

    # args specific to type
    # Sort

    if 'Sort Method' in plan:
        #print('(' + plan['Sort Method'] + ')', end='')
        node['Sort Method']=plan['Sort Method']
        node['Sort Key']=plan['Sort Key']
    # Seq scan
    if 'Relation Name' in plan:
        #print('table:' + plan['Relation Name'] + ' ', end='')
        node['Relation Name']=plan['Relation Name']
    # Aggregate
    if 'Strategy' in plan:
        #print('(' + plan['Strategy'] + ') ', end='')
        node['Strategy'] = plan['Strategy']
    if 'Group Key' in plan:
        #print('GROUP BY ' + str(plan['Group Key']) + ' ', end='')
        node['Group Key']= plan['Group Key']
    if 'Subplan Name' in plan:
        #print('AS ' + plan['Subplan Name'] + ' ', end='')
        node['Subplan Name']=plan['Subplan Name']
    # Seq scan & aggregate
    if 'Filter' in plan:
        #print('filter:' + convert_condition(plan['Filter']) + ' ', end='')
        node['Filter']= convert_condition(plan['Filter'])
    # Hash join
    if 'Hash Cond' in plan:
        #print('cond:' + convert_condition(plan['Hash Cond']) + ' ', end='')
        node['Hash Cond']=process_cond(plan['Hash Cond'])
    # Merge join
    if 'Merge Cond' in plan:
        #print('cond:' + convert_condition(plan['Merge Cond']) + ' ', end='')
        node['Merge Cond']=process_cond(plan['Merge Cond'])
    # Index only scan # this cond most prob used for NL join
    if 'Index Cond' in plan:
        #print('cond:' + convert_condition(plan['Index Cond']) + ' ', end='')
        node['Index Cond']=process_cond(plan['Index Cond'])
    if 'Alias' in plan:
        #print("AS " + plan['Alias'], end='')
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

