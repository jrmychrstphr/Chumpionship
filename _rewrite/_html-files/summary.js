function summary(manager_code){
	if (!(manager_code)) {
        manager_code = '55259'
    }

	// Compile a dataset from the database
    // Total transfers made by gameweek
    dataset = {}            

    //for each player in the database
    $.each( database['player_data'], function(key, val) {

        if (key === manager_code) {

        	position = val.season_performance.league_position_now
        	total_score = val.season_performance.fixture_score_total
        	high_score = d3.max(val.season_performance.fixture_score_array)

    		dataset = {
    			'manager_name': return_manager_fullname(database, manager_code),
    			'team_name': return_team_name(database, manager_code),
                'position': position,
                'total_score': total_score,
                'high_score': high_score
            }
        }

    })

    console.log(dataset)

    d3.select('#page-title .dynamic-content')
    .text( function(d) {
    	t = dataset.manager_name + ' – ' + dataset.team_name
    	return t
    })

    d3.select('#final-league-position div.dynamic-content')
    .text(return_ordinal_suffix_of(dataset.position))

    d3.select('#overall-points-scored div.dynamic-content')
    .text(return_comma_formatted_number(dataset.total_score))
    
    d3.select('#highest-single-score div.dynamic-content')
    .text(return_comma_formatted_number(dataset.high_score))
    

}