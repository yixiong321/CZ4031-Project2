import pickle

with open('query_plans'+'6'+'.pkl', 'rb') as f:
  mynewlist = pickle.load(f)

for plan in mynewlist:
  print(plan)