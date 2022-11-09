import sqlparse
import colorama
from colorama import Fore

count = 0
str0 = "Select l_returnflag,l_linestatus,sum(l_quantity) as sum_qty,sum(l_extendedprice) as sum_base_price,sum(l_extendedprice * (1-l_discount)) as sum_disc_price,sum(l_extendedprice * (1-l_discount) * (1+l_tax)) as sum_charge,avg(l_quantity) as avg_qty,avg(l_extendedprice) as avg_price,avg(l_discount) as avg_disc,count(*) as count_order from lineitem where l_extendedprice < 33000 group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus"
query = "Select * from orders, customer where c_custkey = o_custkey and c_name = 'Cheng' ORDER BY c_phone"
str2 = "select 100.00 * sum(case when p_type like 'PROMO%' then l_extendedprice * (1 - l_discount) else 0 end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue from lineitem, part where l_partkey = p_partkey and l_shipdate >= date '1993-11-01' limit 1;"

sql_keywords = ['SELECT', 'WHERE', 'GROUP BY','ORDER BY', 'EXISTS', 'LIMIT', 'DISTINCT']
list1 = []
list2 = []

#make SQL keywords capital
res = sqlparse.format(query, encoding=None, keyword_case = "upper")
print("\nFORMATTED QUERY:\n" + res)

parsed = sqlparse.parse(res)
print("\nPARSED QUERY:\n" + str(parsed))

stmt = parsed[0]

for i in stmt.tokens:
    list1.append(str(i))

print(list1)
print(len(list1))


row = 0
for i in list1:
    print("iteration for " + i)
    if i in sql_keywords and row == 0:
        list2.append(i)
        
    
    elif i not in sql_keywords:
        if 'WHERE' in i.split(None):
            row+=1
            list2.append(i)
        else: list2[row] += i
    
    elif i in sql_keywords and row != 0:
        row+=1
        list2.append(i)
    print(list2)

for i in list2:
    print(i)


