
#!/usr/bin/python
import psycopg2
import json
from GUI.nodetypes import node_types_dict



def get_unique_node_types_dic(level,dic):
    if level["Node Type"] not in dic:
        dic[level['Node Type']]=0
    if level['Node Type'] in dic:
        dic[level['Node Type']]+=1
    if "Plans" not in level:
        return 
    else:
        for p in level['Plans']:
            get_unique_node_types_dic(p,dic)
    return dic


def get_nodelist(level,lis):
    lis.append(level["Node Type"])
    if "Plans" not in level:
        return 
    else:
        for p in level['Plans']:
            get_nodelist(p,lis)
    return lis

def conversion_for_blockdiag(layer,counter):
    counter+=1
    #stopping condition
    if "Plans" not in layer:
        return ["'"+str(counter)+")"+layer['Node Type']+"';"]
    else:
        str_list = []
        for x in range(len(layer['Plans'])):
            s="'"+str(counter)+")"+layer['Node Type']+"' "+leftArrow
            for rel in conversion_for_blockdiag(layer["Plans"][x],counter):
                str_list.append(s+rel)
        return str_list

def fetch_AQPS(cur,node_types,sqlquery,query_plans):
        aqp_relations=[]
        for key in node_types:
            new_d=[]
            if key in node_types_dict:
                #print(node_types_dict[key])
                cur.execute("SET LOCAL "+node_types_dict[key]+" TO OFF")
                cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + sqlquery)
                rows = cur.fetchall()
                res = json.dumps(rows)
                res=json.loads(res)
                for x in res[0][0]:
                    query_plans.append(x)
                    print('Execution Time:',x['Execution Time'])
                    root = x['Plan']
                    aqp_nodes = get_nodelist(root,new_d)
                    print(aqp_nodes)
                    counter=0
                    res=conversion_for_blockdiag(root,counter)
                    print(res)
                    aqp_relations.append(res)
        return aqp_relations

def process_QEP(rows,query_plans,node_types_d):
    res = json.dumps(rows)
    res = json.loads(res)
    for x in res[0][0]:
        query_plans.append(x)
        print('Execution Time:',x['Execution Time'])
        node_types = get_unique_node_types_dic(x['Plan'],node_types_d)
        print(node_types)
        counter=0
        res=conversion_for_blockdiag(x['Plan'],counter)
        print(res)
    return node_types,res

rightArrow=" -> "
leftArrow=" <- "



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
        for no in range(1,11):
            #filename = 'Queries\q'+str(no)+'.sql'
            #print("Reading "+filename)
            filename = 'Queries\q2.sql'

            fd = open(filename, 'r')
            sqlquery = fd.read()
            fd.close()

            node_types_d = {}
            query_plans = []
            # Getting query plan
            cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + sqlquery)
            rows = cur.fetchall()
            node_types=process_QEP(rows,query_plans,node_types_d)
            
            # fetching AQPS
            fetch_AQPS(cur,node_types.keys(),sqlquery,query_plans)
            #print(query_plans[len(query_plans)-1])    
            print("Total number of query plans: "+str(len(query_plans)))     
            #everything in query_plans     
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

