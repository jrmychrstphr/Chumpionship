var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/_rewrite/2020_season_data%20-%20u.json"

var database;
    
$.getJSON(database_url, function(json) { database = json });