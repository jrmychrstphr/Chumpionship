var filename = '2020_season_data---20200618_0952.json'
var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/_rewrite/"+filename

console.log(database_url)

var database;
    
$.getJSON(database_url, function(json) { database = json });