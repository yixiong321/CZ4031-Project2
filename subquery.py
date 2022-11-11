import sqlparse

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

q22='''select
        cntrycode,
        count(*) as numcust,
        sum(c_acctbal) as totacctbal
from
        (
                select
                        substring(c_phone from 1 for 2) as cntrycode,
                        c_acctbal
                from
                        customer
                where
                        substring(c_phone from 1 for 2) in
                                ('24', '32', '17', '18', '12', '14', '22')
                        and c_acctbal > (
                                select
                                        avg(c_acctbal)
                                from
                                        customer
                                where
                                        c_acctbal > 0.00
                                        and substring(c_phone from 1 for 2) in
                                                ('24', '32', '17', '18', '12', '14', '22')
                        )
                        and not exists (
                                select
                                        *
                                from
                                        orders
                                where
                                        o_custkey = c_custkey
                        )
        ) as custsale
group by
        cntrycode
order by
        cntrycode;'''
sqlquery = sqlparse.format(q2,encoding=None,keyword_case='upper')

sql=sqlquery.replace('\t','').replace('AND ','').split('\n')
for x in range(len(sql)):
    sql[x]=sql[x].lstrip()

print(sql)

class line():
    def __init__(self,query_term,line_number,subquery_number):
        self.query_term=query_term
        self.line_number=line_number
        self.subquery_number=subquery_number

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
for i in sql_query_list:
    print(i.line_number,i.query_term,i.subquery_number)