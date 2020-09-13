//var filename = '2020_season_data---20200618_1022.json'
var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/seasons/2021/database/_versions/chumpionship_2021_database-new-history-fixtures.json"

var database;
    
$.getJSON(database_url, function(json) { database = json });