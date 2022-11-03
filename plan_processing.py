
import sqlglot 
import sqlparse
res1 = [([{'Plan': {
    'Node Type': 'Aggregate', 
    'Strategy': 'Sorted', 
    'Partial Mode': 'Finalize', 
    'Parallel Aware': False, 
    'Async Capable': False, 
    'Startup Cost': 184927.59, 
    'Total Cost': 184929.54, 
    'Plan Rows': 6, 
    'Plan Width': 236, 
    'Actual Startup Time': 1832.355, 
    'Actual Total Time': 1840.507, 
    'Actual Rows': 4, 
    'Actual Loops': 1, 
    'Output': ['l_returnflag', 'l_linestatus', 'sum(l_quantity)', 'sum(l_extendedprice)', "sum((l_extendedprice * ('1'::numeric - l_discount)))",
     "sum(((l_extendedprice * ('1'::numeric - l_discount)) * ('1'::numeric + l_tax)))", 'avg(l_quantity)', 'avg(l_extendedprice)', 'avg(l_discount)', 'count(*)'], 
    'Group Key': ['lineitem.l_returnflag', 'lineitem.l_linestatus'], 
    'Plans': [
        {'Node Type': 'Gather Merge',
         'Parent Relationship': 'Outer', 
         'Parallel Aware': False, 
         'Async Capable': False, 
         'Startup Cost': 184927.59, 
         'Total Cost': 184928.99, 
         'Plan Rows': 12, 
         'Plan Width': 236, 
         'Actual Startup Time': 1832.33, 
         'Actual Total Time': 1840.464, 
         'Actual Rows': 12, 
         'Actual Loops': 1, 
         'Output': ['l_returnflag', 'l_linestatus', '(PARTIAL sum(l_quantity))', '(PARTIAL sum(l_extendedprice))', "(PARTIAL sum((l_extendedprice * ('1'::numeric - l_discount))))", 
         "(PARTIAL sum(((l_extendedprice * ('1'::numeric - l_discount)) * ('1'::numeric + l_tax))))", '(PARTIAL avg(l_quantity))',
         '(PARTIAL avg(l_extendedprice))', '(PARTIAL avg(l_discount))', '(PARTIAL count(*))'], 
         'Workers Planned': 2, 
         'Workers Launched': 2,
         'Plans': [
            {'Node Type': 'Sort',
            'Parent Relationship': 'Outer', 
            'Parallel Aware': False, 
            'Async Capable': False, 
            'Startup Cost': 183927.56, 
            'Total Cost': 183927.58, 
            'Plan Rows': 6, 
            'Plan Width': 236, 
            'Actual Startup Time': 1793.031, 
            'Actual Total Time': 1793.032, 
            'Actual Rows': 4, 
            'Actual Loops': 3, 
            'Output': ['l_returnflag', 'l_linestatus', '(PARTIAL sum(l_quantity))', '(PARTIAL sum(l_extendedprice))',
             "(PARTIAL sum((l_extendedprice * ('1'::numeric - l_discount))))", "(PARTIAL sum(((l_extendedprice * ('1'::numeric - l_discount)) * ('1'::numeric + l_tax))))", '(PARTIAL avg(l_quantity))',
              '(PARTIAL avg(l_extendedprice))', '(PARTIAL avg(l_discount))', '(PARTIAL count(*))'],
            'Sort Key': ['lineitem.l_returnflag', 'lineitem.l_linestatus'], 
            'Sort Method': 'quicksort', 
            'Sort Space Used': 27, 
            'Sort Space Type': 'Memory', 
            'Workers': [{
                'Worker Number': 0, 
                'Actual Startup Time': 1773.887, 
                'Actual Total Time': 1773.888, 
                'Actual Rows': 4, 
                'Actual Loops': 1, 
                'Sort Method': 'quicksort', 
                'Sort Space Used': 27, 
                'Sort Space Type': 'Memory'},
                 {'Worker Number': 1, 
                 'Actual Startup Time': 1773.547, 
                 'Actual Total Time': 1773.548, 
                 'Actual Rows': 4, 
                 'Actual Loops': 1, 
                 'Sort Method': 'quicksort', 
                 'Sort Space Used': 27, 
                 'Sort Space Type': 'Memory'}
                 ], 
            'Plans': [
                {'Node Type': 'Aggregate', 
                'Strategy': 'Hashed', 
                'Partial Mode': 'Partial', 
                'Parent Relationship': 'Outer', 
                'Parallel Aware': False, 
                'Async Capable': False, 
                'Startup Cost': 183927.35, 
                'Total Cost': 183927.49, 
                'Plan Rows': 6, 
                'Plan Width': 236, 
                'Actual Startup Time': 1792.837, 
                'Actual Total Time': 1792.843, 
                'Actual Rows': 4, 
                'Actual Loops': 3,
                'Output': ['l_returnflag', 'l_linestatus', 'PARTIAL sum(l_quantity)', 'PARTIAL sum(l_extendedprice)', "PARTIAL sum((l_extendedprice * ('1'::numeric - l_discount)))",
                 "PARTIAL sum(((l_extendedprice * ('1'::numeric - l_discount)) * ('1'::numeric + l_tax)))", 'PARTIAL avg(l_quantity)', 'PARTIAL avg(l_extendedprice)',
                  'PARTIAL avg(l_discount)', 'PARTIAL count(*)'], 'Group Key': ['lineitem.l_returnflag', 'lineitem.l_linestatus'], 
                  'Planned Partitions': 0, 
                  'HashAgg Batches': 1, 
                  'Peak Memory Usage': 32, 
                  'Disk Usage': 0, 
                  'Workers': [
                    {'Worker Number': 0, 
                    'Actual Startup Time': 1773.719, 
                    'Actual Total Time': 1773.725, 
                    'Actual Rows': 4, 
                    'Actual Loops': 1, 
                    'HashAgg Batches': 1, 
                    'Peak Memory Usage': 32, 
                    'Disk Usage': 0}, 
                    {'Worker Number': 1, 
                    'Actual Startup Time': 1773.168, 
                    'Actual Total Time': 1773.173, 
                    'Actual Rows': 4, 
                    'Actual Loops': 1, 
                    'HashAgg Batches': 1, 
                    'Peak Memory Usage': 32, 
                    'Disk Usage': 0}], 
                    'Plans': [{
                        'Node Type': 'Seq Scan', 
                        'Parent Relationship': 'Outer', 
                        'Parallel Aware': True,
                         'Async Capable': False, 
                         'Relation Name': 'lineitem', 
                         'Schema': 'public', 'Alias': 'lineitem', 
                         'Startup Cost': 0.0, 
                         'Total Cost': 144526.03, 
                         'Plan Rows': 1125752, 
                         'Plan Width': 25, 
                         'Actual Startup Time': 0.788, 
                         'Actual Total Time': 700.398, 
                         'Actual Rows': 896396, 
                         'Actual Loops': 3, 
                         'Output': ['l_orderkey', 'l_partkey', 'l_suppkey', 'l_linenumber', 'l_quantity', 
                         'l_extendedprice', 'l_discount', 'l_tax', 'l_returnflag', 'l_linestatus', 'l_shipdate', 
                         'l_commitdate', 'l_receiptdate', 'l_shipinstruct', 'l_shipmode', 'l_comment'], 
                         'Filter': "(lineitem.l_extendedprice < '33000'::numeric)", 
                         'Rows Removed by Filter': 1104009, 
                         'Workers': [
                            {'Worker Number': 0, 'Actual Startup Time': 0.827, 'Actual Total Time': 661.707, 'Actual Rows': 909164, 'Actual Loops': 1},
                             {'Worker Number': 1, 'Actual Startup Time': 0.483, 'Actual Total Time': 691.059, 'Actual Rows': 901847, 'Actual Loops': 1}
                             ]}]}]}]}]},
                              'Planning Time': 1.563, 'Triggers': [], 'Execution Time': 1840.708}],)]


sql_query ='''
            select
                l_returnflag,
                l_linestatus,
                sum(l_quantity) as sum_qty,
                sum(l_extendedprice) as sum_base_price,
                sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
                sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
                avg(l_quantity) as avg_qty,
                avg(l_extendedprice) as avg_price,
                avg(l_discount) as avg_disc,
                count(*) as count_order
            from
                lineitem
            where
                l_extendedprice < 33000
            group by
                l_returnflag,
                l_linestatus
            order by
                l_returnflag,
                l_linestatus

            '''

res2 = [[[
    {"Plan": {"Node Type": "Limit", "Parallel Aware": False, "Async Capable": False, 
    "Startup Cost": 60248.82, "Total Cost": 154077.97, "Plan Rows": 1, "Plan Width": 24, "Actual Startup Time": 66763.502, "Actual Total Time": 66773.444, "Actual Rows": 1, "Actual Loops": 1, "Output": ["orders.o_orderpriority", "(count(*))"], 
    "Plans": [
    {"Node Type": "Aggregate", 
    "Strategy": "Sorted",
     "Partial Mode": "Simple", "Parent Relup Time": 66763.5, 
     "Actual Total Time": 66773.442, "Actual Rows": 1, "Actual Loops": 1,
      "Output": ["orders.o_orderpriority", "count(*)"],
       "Group Key": ["orders.o_orderpriority"],
        "Plans": [
            {"Node Type": "Nested Loop", "Parent Relationship": "Outer",
             "Parallel Aware": False,
              "Async Capable": False, 
              "Join Type": "Semi", 
              "Startup Cost": 60248.82,
               "Total Cost": 528721.76,
                "Plan Rows": 134556,
                 "Plan Width": 16, "Actual Startup Time": 11509.371,
                  "Actual Total Time": 66619.235, "Actual Rows": 101615,
                   "Actual Loops": 1, "Output": ["orders.o_orderpriority"],
                    "Inner Unique": False, "Plans": [{"Node Type": "Gather Merge", 
                    "Parent Relationship": "Outer", 
                    "Parallel Aware": False,
                     "Async Capable": False,
                      "Startup Cost": 60248.39,
                       "Total Cost": 124478.02, "Plan Rows": 551486, "Plan Width": 20,
                        "Actual Startup Time": 11509.341, "Actual Total Time": 11980.239,
                         "Actual Rows": 110736, "Actual Loops": 1,
                          "Output": ["orders.o_orderpriority", "orders.o_orderkey"], 
                          "Workers Planned": 2, "Workers Launched": 2,
                           "Plans": [{
                            "Node Type": "Sort", 
                           "Parent Relationship": "Outer", 
                           "Parallel Aware": False,
                            "Async Capable": False, "Startup Cost": 59248.36,
                             "Total Cost": 59822.83, 
                             "Plan Rows": 229786, 
                             "Plan Width": 20, 
                             "Actual Startup Time": 11456.533, 
                             "Actual Total Time": 11491.601, "Actual Rows": 37723,
                              "Actual Loops": 3, 
                              "Output": ["orders.o_orderpriority", "orders.o_orderkey"], 
                              "Sort Key": ["orders.o_orderpriority"], 
                              "Sort Method": "external merge",
                               "Sort Space Used": 5712, "Sort Space Type": "Disk",
                                "Workers": [{"Worker Number": 0, "Actual Startup Time": 11438.885, "Actual Total Time": 11458.749, "Actual Rows": 37959, "Actual Loops": 1, "Sort Method": "external merge",
                                 "Sort Space Used": 5376, "Sort Space Type": "Disk"},
                                  {"Worker Number": 1, "Actual Startup Time": 11435.467,
                                   "Actual Total Time": 11453.362, "Actual Rows": 36249, "Actual Loops": 1,
                                    "Sort Method": "external merge", "Sort Space Used": 5152, "Sort Space Type": "Disk"}],
                                     "Plans": [{"Node Type": "Seq Scan", "Parent Relationship": "Outer",
                                      "Parallel Aware": True, "Async Capable": False, "Relation Name": "orders", "Schema": "public",
                                       "Alias": "orders", "Startup Cost": 0.0, "Total Cost": 34071.5,
                                        "Plan Rows": 229786, "Plan Width": 20, "Actual Startup Time": 3.128,
                                         "Actual Total Time": 11270.596, "Actual Rows": 184189, "Actual Loops": 3,
                                          "Output": ["orders.o_orderpriority", "orders.o_orderkey"],
                                           "Filter": "(orders.o_orderdate >= '1996-03-01'::date)",
                                            "Rows Removed by Filter": 315811,
                                             "Workers": [{"Worker Number": 0, "Actual Startup Time": 3.731, "Actual Total Time": 11262.314, "Actual Rows": 183032,
                                              "Actual Loops": 1}, {"Worker Number": 1, "Actual Startup Time": 5.632,
                                               "Actual Total Time": 11271.859, "Actual Rows": 175168, "Actual Loops": 1}]}]}]},
                                                {"Node Type": "Index Scan", "Parent Relationship": "Inner", "Parallel Aware": False,
                                                 "Async Capable": False, "Scan Direction": "Forward", "Index Name": "lineitem_pkey", 
                                                 "Relation Name": "lineitem", "Schema": "public", "Alias": "lineitem",
                                                  "Startup Cost": 0.43, "Total Cost": 1.74, "Plan Rows": 5, "Plan Width": 4,
                                                   "Actual Startup Time": 0.491, "Actual Total Time": 0.491, "Actual Rows": 1,
                                                    "Actual Loops": 110736, "Output": ["lineitem.l_orderkey", "lineitem.l_partkey",
                                                     "lineitem.l_suppkey", "lineitem.l_linenumber", "lineitem.l_quantity",
                                                      "lineitem.l_extendedprice", "lineitem.l_discount", "lineitem.l_tax",
                                                       "lineitem.l_returnflag", "lineitem.l_linestatus", "lineitem.l_shipdate",
                                                        "lineitem.l_commitdate", "lineitem.l_receiptdate", "lineitem.l_shipinstruct", 
                                                        "lineitem.l_shipmode", "lineitem.l_comment"], 
                                                        "Index Cond": "(lineitem.l_orderkey = orders.o_orderkey)", 
                                                        "Rows Removed by Index Recheck": 0, "Filter": "(lineitem.l_commitdate < lineitem.l_receiptdate)", "Rows Removed by Filter": 1}]}]}]}, "Planning Time": 93.291, "Triggers": [], "Execution Time": 66775.494}]]]


# gen a tree first?
'''
def traverse_plans(plan):
    if "Plans" not in plan.keys():
        return {'Node Type':plan['Node Type']}
    else:
        node = {'Node Type':plan['Node Type'],'children':[]}
        for p in plan['Plans']:
            node['children'].append(traverse_plans(p))
        return node


for x in res2[0][0]:
    print('Execution Time:',x['Execution Time'])
    # Plan lvl 
    root = x['Plan']
    rootnode={'Node Type':root['Node Type'],'children':[]}
    print(root.keys())
    tree = traverse_plans(root)
    print(tree)
'''
sql2 = '''
select
	o_orderpriority,
	count(*) as order_count
from
	orders
where
	o_orderdate >= date '1996-03-01'
	and exists (
		select
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
def recursiveStanza(self,layer):
    #stopping condition
    if len(layer.children)==0:
        return {'name':layer.label}
    else:
        lvl={'name':layer.label,'children':[]}
        for x in range(len(layer.children)):
                lvl['children'].append(self.recursiveStanza(layer.children[x]))
        return lvl
    
rightArrow=" -> "
leftArrow=" <- "
def get_unique_node_types(level):
    if "Plans" not in level:
        return "'"+str(level['Node Type'])+"';"
    else:
        total=""
        s="'"+level['Node Type']+"' "
        for p in level['Plans']:
            total=total+s+leftArrow+get_unique_node_types(p)

    return total

counter=7
def conversion_for_blockdiag(layer,counter):
    counter-=1
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
for x in res2[0][0]:
    print('Execution Time:',x['Execution Time'])
    # Plan lvl 
    root = x['Plan']
    #print(root.keys())
    res = conversion_for_blockdiag(root,counter)
    print(res)





