<script>
	var database_url = "https://raw.githubusercontent.com/jrmychrstphr/Chumpionship/master/seasons/2022/database/chumpionship_2022_database.json"
	var database;
	    
	$.getJSON(database_url, function(json) { database = json });
</script>