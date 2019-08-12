x = ['<td>26</td>', '<td class="MatchesTable__MatchesEntry1-sc-1p0h4g1-8 kvxgCL"><strong>Clarendon Drovers</strong><br/>James Hunter</td>', '<td class="MatchesTable__MatchesScore-sc-1p0h4g1-10 ujSSI">v</td>', '<td class="MatchesTable__MatchesEntry2-sc-1p0h4g1-9 cMsXSV"><strong>Pepe in our step</strong><br/>Lee Guthrie</td>']

#find the gameweek
string_start = "<td>"
string_start_pos = x[0].find(string_start)
string_start_pos = string_start_pos + len(string_start)
print("string_start", string_start_pos)

string_end_pos = x[0].find("</td>")
print("string_end", string_end_pos)

string = x[0][string_start_pos:string_end_pos]
print(string)


#find player name 1
string_start = "</strong><br/>"
string_start_pos = x[1].find(string_start)
string_start_pos = string_start_pos + len(string_start)
print("string_start", string_start_pos)

string_end_pos = x[1].find("</td>")
print("string_end", string_end_pos)

string = x[1][string_start_pos:string_end_pos]
print(string)

#find player name 2
string_start = "</strong><br/>"
string_start_pos = x[3].find(string_start)
string_start_pos = string_start_pos + len(string_start)
print("string_start", string_start_pos)

string_end_pos = x[3].find("</td>")
print("string_end", string_end_pos)

string = x[3][string_start_pos:string_end_pos]
print(string)