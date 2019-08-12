import json

f = open("../json/2020_database_temp.json")
data = json.load(f)
f.close()

names = []


for key in data:
    
    #create a list of key names
    names.append(key)
    
print(names)

for n in names:
    new = {}
    new = data[n]
    
    del data[n]
    
    lowercase_name = n.lower()
    
    data[lowercase_name] = new
    
with open("../json/2020_database_temp.json", 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))