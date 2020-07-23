//var filename = '2020_season_data---20200618_1022.json'
var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/Mean%20Goals/2020_season_data---20200719_0026.json"

var database;
    
$.getJSON(database_url, function(json) { database = json });