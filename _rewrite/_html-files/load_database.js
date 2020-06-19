var filename = '2020_season_data---20200618_1022.json'
var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/_rewrite/"+filename

var database;
    
$.getJSON(database_url, function(json) { database = json });