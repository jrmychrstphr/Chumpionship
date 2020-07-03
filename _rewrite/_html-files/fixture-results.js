function fixture_results(manager_code) {


    if (!(manager_code)) {
        manager_code = '55259'
    }
    // Compile a dataset from the database
    var dataset = []

    $.each( database['player_data'], function(key, val) {

        if ( key === manager_code) {
            $.each( val.gw_performance, function(k,v) {

                gameweek = k
                score = v.fixture_score
                result = v.fixture_result
                opponent_team_name = v.fixture_opponent_team_name
                opponent_score = return_fixture_score(database, v.fixture_opponent_manager_code, gameweek)

                temp_obj = {
                    'gameweek': parseInt(gameweek),
                    'score': score,
                    'result': result,
                    'opponent_team_name': opponent_team_name,
                    'opponent_score': opponent_score,
                    'margin': score - opponent_score

                }

                dataset.push(temp_obj)
            } )
        }

        dataset = dataset.slice().sort((a, b) => d3.ascending(a.gameweek, b.gameweek))

    });

    console.log(dataset)

    var viz_container = d3.select("#fixture-results .dynamic-content")

    var fixture_rows = viz_container.selectAll(".fixture")
    .data(dataset.slice().sort((a, b) => d3.ascending(a.gameweek, b.gameweek)))
    .enter()
    .append('div')
    .classed('fixture', true)
    .classed('table-row', true)
    .style('border-color', chump_colours.dark_grey);


    fixture_rows.each(function(d) {

        // indicator
        var indicator = d3.select(this).append('div')
        .classed('table-column', true)
        .classed('indicator', true)
        .style('background-color', function(d) {

            if (d.result === 'D') {
                f = chump_colours.grey
            } else if (d.result === 'W') {
                f = chump_colours.green
            } else if (d.result === 'L') {
                f = chump_colours.blue
            } else {
                f = 'Black'
            }      

            return f  

        })

/*
        indicator.append('svg')
        .attr('height', 20)
        .attr('width', 20)
        .append('circle')
        .attr('cx', 10)
        .attr('cy', 10)
        .attr('r', 6)
        .style('fill', function(d) {

            

            return f
        })
*/

        // gameweek
        d3.select(this).append('div')
        .classed('table-column', true)
        .text( function(d) {
            text = "GW" + d.gameweek
            return text
        } )

        // score
        d3.select(this).append('div')
        .classed('table-column', true)
        .text( function(d) {

            s = d.score
            o = d.opponent_score

            text = s + " – " + o

            return text

        } )


        // result
        d3.select(this).append('div')
        .classed('table-column', true)
        .text( function(d) {

            r = d.result

            if ( r === "D" ) {
                text = "Draw"
            } else if ( r === "W" ) {
                text = "Win"
            } else if ( r === "L" ) {
                text = "Loss"
            } else {
                text = "Err"
            }

            return text
        } )


        // opponent
        d3.select(this).append('div')
        .classed('table-column', true)
        .text( function(d) {
            o = d.opponent_team_name
            text = 'vs ' + o

            return text
        } )

    })


}