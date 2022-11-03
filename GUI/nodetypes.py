


node_types_dict={
    'Aggregate': 'ENABLE_HASHAGG',
    'Gather Merge': 'ENABLE_GATHERMERGE',
    'Sort': 'ENABLE_SORT',
    'Seq Scan': 'ENABLE_SEQSCAN',
    #'Limit': 'Limit',
    'Nested Loop': 'ENABLE_NESTLOOP',
    'Index Scan': 'ENABLE_INDEXSCAN',
    'Hash Join': 'ENABLE_HASHJOIN', 
    #'Hash': 'Hash', 
    'Merge Join': 'ENABLE_MERGEJOIN', 
    'Incremental Sort': 'ENABLE_INCREMENTAL_SORT', 
    'Memoize': 'ENABLE_MEMOIZE', 
    'Materialize': 'ENABLE_MATERIAL', 
    #'Gather': 'Gather'
     }        
#note that setting this will not totally remove it,but only push it as a the last resort.
AQP_configs=['ENABLE_BITMAPSCAN','ENABLE_GATHERMERGE','ENABLE_HASHAGG','ENABLE_HASHJOIN',
'ENABLE_INCREMENTAL_SORT','ENABLE_INDEXSCAN','ENABLE_INDEXONLYSCAN','ENABLE_MERGEJOIN',
'ENABLE_NESTLOOP','ENABLE_MATERIAL','ENABLE_MEMOIZE',
'ENABLE_PARALLEL_HASH','ENABLE_SEQSCAN','ENABLE_SORT']

