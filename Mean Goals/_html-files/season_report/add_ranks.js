function add_ranks(manager_code){
    
	if (!(manager_code)) {
        manager_code = '55259'
    }

	// Compile a dataset from the database
    // Total transfers made by gameweek
    dataset = []           

    //for each player in the database
    $.each( database['player_data'], function(key, val) {

    		temp_obj = {
    			'manager_code': key,
                'overall_score': d3.sum(val.season_performance.fixture_score_array),
                'highest_score': d3.max(val.season_performance.fixture_score_array),
                'lowest_score': d3.min(val.season_performance.fixture_score_array),
                'transfers': d3.sum(val.season_performance.transfers_made_array),
                'points_spent': d3.sum(val.season_performance.points_spent_array),
                'average_position': d3.mean(val.season_performance.league_position_array)

            }


        dataset.push(temp_obj)

    })   

    console.log(dataset) 

    rank_dataset = []

    $.each(dataset,function(idx,v) {

        $.each(v,function(key,val) {

            if ( key != 'manager_code' ) {

                var prev_val = ""

                $.each( dataset.slice().sort((a, b) => d3.ascending(a.key, b.key)), function(idx, val) {

                }

            }


        })

    })

}