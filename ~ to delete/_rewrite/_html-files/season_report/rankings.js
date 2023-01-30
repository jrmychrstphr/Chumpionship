function ranks(manager_code) {

    if (!(manager_code)) {
        manager_code = '55259'
    }

	// Compile a dataset from the database
    // Total transfers made by gameweek
    dataset = []

    function create_new_obj() {

        o = {
            'overall_score': [],
            'points_on_bench': [],
            'high_scores': [],
            'low_scores': [],
            'average_league_pos': [],
            'transfers_made': [],
            'points_spent': []
        }

        return o

    }

    temp_arrays = create_new_obj()
    player_values = create_new_obj()

    //for each player in the database
    $.each( database['player_data'], function(key, val) {

        //Push to temp arrays
        //Overall score
        temp_arrays.overall_score.push(val.season_performance.fixture_score_total)
        //Total points on bench
        temp_arrays.points_on_bench.push(val.season_performance.points_on_bench_total)
        //Highest single score
        temp_arrays.high_scores.push(d3.max(val.season_performance.fixture_score_array))
        //Lowest single score
        temp_arrays.low_scores.push(d3.min(val.season_performance.fixture_score_array))
        //Average league position
        temp_arrays.average_league_pos.push(parseFloat(d3.format(".1f")(d3.mean(val.season_performance.league_position_array))))
        //Total transfers made
        temp_arrays.transfers_made.push(val.season_performance.transfers_made_total)
        //Total points spent
        temp_arrays.points_spent.push(val.season_performance.points_spent_total)

        if ( key === manager_code ) {

            player_values.overall_score = val.season_performance.fixture_score_total
            player_values.points_on_bench = val.season_performance.points_on_bench_total
            player_values.high_scores = d3.max(val.season_performance.fixture_score_array)
            player_values.low_scores = d3.min(val.season_performance.fixture_score_array)
            player_values.average_league_pos = parseFloat(d3.format(".1f")(d3.mean(val.season_performance.league_position_array)))
            player_values.transfers_made = val.season_performance.transfers_made_total
            player_values.points_spent = val.season_performance.points_spent_total

        }

    })

    player_ranks = create_new_obj()

    $.each( temp_arrays, function(key, val) {

        if ( key === 'low_scores' || key === 'average_league_pos') {
            ordered_array = val.sort(d3.ascending)
        } else {
        ordered_array = val.sort(d3.descending)
        }

        player_ranks[key] = val.indexOf(player_values[key]) + 1


    })

    console.log(player_ranks)


    //add to DOM
    //Overall score
    d3.select('#overall-points-scored-1 div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.overall_score))

    d3.select('#overall-points-scored-2 div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.overall_score))

    //Total points on bench
    d3.select('#points-on-bench div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.points_on_bench))

    //Highest single score
    d3.select('#highest-score-1 div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.high_scores))

    d3.select('#highest-score-2 div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.high_scores))

    //Lowest single score
    d3.select('#lowest-score div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.low_scores))

    //Average league position
    d3.select('#average-league-position div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.average_league_pos))

    //Total transfers made
    d3.select('#total-transfers div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.transfers_made))

    //Total points spent
    d3.select('#total-points-spent div.dynamic-content') 
    .append('span')
    .classed('rank', true)
    .text(return_ordinal_suffix_of(player_ranks.points_spent))

}