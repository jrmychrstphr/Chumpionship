//var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/seasons/2021/database/chumpionship_2021_database.json"
var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/seasons/2022/database/2022_database.json"
var database;
    
$.getJSON(database_url, function(json) { database = json });