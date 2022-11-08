
#!/usr/bin/python
import psycopg2
import json
from pathlib import Path

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
            password="123")
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
        query = Path('Queries/q10.sql').read_text()
        cur.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + query)
        rows = cur.fetchall()
        x = json.dumps(rows)
        print(x)
        print()
        for a in rows[0][0]:
            display(a['Plan'])
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def display(plan, level=0):
    print('    ' * level, end='')
    if 'Join Type' in plan:# Loop/Join
        print(plan['Join Type'] + ' ', end='')
    print(plan['Node Type'] + ' ', end='')

    explore(plan) # trying to find interesting keys

    # args specific to type
    # Sort
    if 'Sort Method' in plan:
        print('(' + plan['Sort Method'] + ')', end='')
    # Seq scan
    if 'Relation Name' in plan:
        print('table:' + plan['Relation Name'] + ' ', end='')
    # Aggregate
    if 'Strategy' in plan:
        print('(' + plan['Strategy'] + ') ', end='')
    if 'Group Key' in plan:
        print('BY ' + str(plan['Group Key']) + ' ', end='')
    if 'Subplan Name' in plan:
        print('AS ' + plan['Subplan Name'] + ' ', end='')
    # Seq scan & aggregate
    if 'Filter' in plan:
        print('filter:' + plan['Filter']
        .replace('::numeric','')
        .replace('::bpchar','')
        .replace('::date','')
        + ' ', end='')
    # Hash join
    if 'Hash Cond' in plan:
        print('cond:' + plan['Hash Cond'] + ' ', end='')
    # Merge join
    if 'Merge Cond' in plan:
        print('cond:' + plan['Merge Cond'] + ' ', end='')
    # Index only scan
    if 'Index Cond' in plan:
        print('cond:' + plan['Index Cond'] + ' ', end='')

    if 'Alias' in plan:
        print("AS " + plan['Alias'], end='')
    print()
    if 'Plans' in plan:
        for p in plan['Plans']:
            display(p,level + 1)

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


connect()