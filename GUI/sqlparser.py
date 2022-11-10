import sqlparse
import colorama
from colorama import Fore

count = 0
str0 = "Select l_returnflag,l_linestatus,sum(l_quantity) as sum_qty,sum(l_extendedprice) as sum_base_price,sum(l_extendedprice * (1-l_discount)) as sum_disc_price,sum(l_extendedprice * (1-l_discount) * (1+l_tax)) as sum_charge,avg(l_quantity) as avg_qty,avg(l_extendedprice) as avg_price,avg(l_discount) as avg_disc,count(*) as count_order from lineitem where l_extendedprice < 33000 group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus"
query = "Select * from orders, customer where c_custkey = o_custkey and c_name = 'Cheng' ORDER BY c_phone"
str2 = "select 100.00 * sum(case when p_type like 'PROMO%' then l_extendedprice * (1 - l_discount) else 0 end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue from lineitem, part where l_partkey = p_partkey and l_shipdate >= date '1993-11-01' limit 1;"

sql_keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY','ORDER BY', 'EXISTS', 'LIMIT', 'DISTINCT']
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

print("this is list1")
print(list1)
print("length of list1: "+ str(len(list1)))
print()


row = 0
for i in list1:
    # print("iteration for " + i)
    if i in sql_keywords and row == 0:
        list2.append(i)
        row+=1
        
    
    elif i not in sql_keywords:
        if 'WHERE' in i.split(None):
            row+=1
            list2.append(i)
        else: list2[row-1] += i
    
    elif i in sql_keywords and row != 0:
        row+=1
        list2.append(i)
    # print(list2)

for i in list2:
    print(i)

# print(len(list2))
# # row = 0
# for i in list1:
#     c = str(i)

#     if c in sql_keywords and row == 0:
#         list1.append(c)
        
    
#     elif c not in sql_keywords:
#         list1[row] += c
    
#     elif c in sql_keywords and row != 0:
#         row+=1
#         list1.append(str(i))

# print(len(list1))
    




# i = 0
# while(i <=11 ):
#     print(stmt.tokens[i])
#     i +=1
#print(stmt) prints whole SQL query
#print(stmt.tokens[0]) prints SELECT
#print(len(stmt))
#for i in stmt:
 #   list1.append(stmt.tokens[i])

#print(list1)



#make SQL keywords capital
#res = sqlparse.format(str2, encoding=None, reindent = True, keyword_case = "upper") #reindent_aligned gives hierarchical alignment
#x = res.split("\n")
#print(x)
#print(res)

#make attributes capital
#res = sqlparse.format(str1,encoding=None, , identifier_case = "upper")
#print(res)





 