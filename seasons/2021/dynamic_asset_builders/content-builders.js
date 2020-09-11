/* content-builders.js */
function build_table(gw) {

    // add this to database
    league_config = {}; league_config.prizes = 4; league_config.relegation = 3;

    //define gameweek
    if (!(gw)) {
        gw = 31
    }

    gameweek = return_gameweek_string(gw)

    //build title block
    var title_container = d3.select("#title-block")
    .append("div")
    .classed("title-wrapper", true)
    .append("div")
    .classed("title-container", true)

    var title = title_container.append("div")
    .classed("text display large", true)
    .text("Standings")

    var subtitle = title_container.append("div")
    .classed("text display regular", true)
    .text("GW" + gw)

    dataset = []

    $.each( database.player_data, function(k, v) {

        temp_obj = {}

        temp_obj.manager_code = k
        temp_obj.position = parseInt(v.season_performance.league_position_array[parseInt(gw)-1])

        if (gw === 1 ) {
            temp_obj.change = 0
        } else {
            temp_obj.change = parseInt(v.season_performance.league_position_array[parseInt(gw)-1]) - parseInt(v.season_performance.league_position_array[parseInt(gw)-2])
        }

        temp_obj.score = v.season_performance.fixture_score_running_total_array[gw-1]
        temp_obj.league_points = v.season_performance.league_points_running_total_array[gw-1]

        temp_obj.form = []

        for (i=0; i<5; i++) {

            if (gw - i > 0) {
                //console.log(gw-(i+1))
                temp_obj.form.unshift(v.season_performance.result_array[gw-(i+1)])
            } else {
                temp_obj.form.unshift("None")
            }

        }

        dataset.push(temp_obj)

    })

    dataset = dataset.slice().sort((a, b) => d3.descending(a.league_points, b.league_points) || d3.descending(a.score, b.score))

    //build content
    var viz_container = d3.select("#content-block")
    .append("div")
    .classed("league-table-wrapper", true)
    .append("div")
    .classed("league-table-container", true)

    var table_rows = viz_container.selectAll("div.table-row-wrapper")
    .data(dataset).enter()
    .append("div")
    .classed("table-row-wrapper", true)
    .append("div")
    .classed("table-row-container", true)
    .each( function(d, i){

        if ( d.position === 1 ) {
            d3.select(this).classed("position-first", true)
        } else if ( d.position <= league_config.prizes ) {
            d3.select(this).classed("position-prize", true)
        } else if ( d.position >= dataset.length - league_config.prizes + 2 ) {
            d3.select(this).classed("position-relegation", true)
        }

        if ( d.change != 0 ) {

            var change = d3.select(this)
            .append("div")
            .classed("position-change-wrapper", true)
            .append("div")
            .classed("position-change-container", true)

            if ( d.change < 0 ) {
                // up arrow
                change.classed("arrow-up", true)
            } else if ( d.change > 0 ) {
                //down arrow
                change.classed("arrow-down", true)
            }

            arrow = change.html(chump.svg.arrow)

        }


        d3.select(this)
        .append("div")
        .classed("table-column position text display regular", true)
        .text(function (d) {

            if ( d.position != (i+1)) {
                t = "="
            } else {
                t = d.position
            }

            return t
        })
        
        d3.select(this)
        .append("div")
        .classed("table-column team-name text display regular", true)
        .text(db_return_team_name(database, d.manager_code))
        
        d3.select(this)
        .append("div")
        .classed("table-column score text display regular", true)
        .text(return_comma_formatted_number(d.score))
        
        var points = d3.select(this)
        .append("div")
        .classed("table-column league-points text display regular", true)
        .text(return_comma_formatted_number(d.league_points))

        points.append("span")
        .classed("display small", true)
        .text("pts")
        
        var form = d3.select(this)
        .append("div")
        .classed("table-column form viz", true)

        //add viz
        viz_container = form

        config = {
            "width": $(this).find(".viz").width(),
            "height": $(this).find(".viz").height()
        }

        svg = viz_container.append("svg")
        .attr("height", config.height)
        .attr("width", config.width)
        .attr("viewBox","0 0 " + config.width + " " + config.height)

        // set scales
        var xDomain = function() {
            a  = []
            for (var i = 0; i < d.form.length; i++) {
                a.push(i);
            }
            return a
        } ()

        xScale = d3.scaleBand()
        .domain(xDomain)
        .range([0, config.width])
        .paddingInner(0)

        // add data
        var data_groups = svg.selectAll("g")
        .data(d.form)
        .enter()
        .append("g")

        data_groups.each( function(d,i) {

            d3.select(this).append("circle")
            .attr("cx", xScale(i) + xScale.bandwidth()/2 )
            .attr("cy", config.height/2 - 9)
            .attr("r", 5 )
            .style("fill", function(d) {
                if ( d === "W" ) {
                    f = chump.colours.green
                } else if ( d === "L" ) {
                    f = chump.colours.pink
                } else if ( d === "D" ) {
                    f = chump.colours.light_blue
                } else {
                    f = "Black"
                }

                return f
            })

            d3.select(this).append("circle")
            .attr("cx", xScale(i) + xScale.bandwidth()/2 )
            .attr("cy", config.height/2 + 9)
            .attr("r", 5 )
            .style("fill", function(d) {
                if ( d === "W" ) {
                    f = chump.colours.green
                } else if ( d === "L" ) {
                    f = chump.colours.pink
                } else if ( d === "D" ) {
                    f = chump.colours.light_blue
                } else {
                    f = "Black"
                }

                return f
            })

            d3.select(this).append("line")
            .attr("x1", xScale(i) + xScale.bandwidth()/2 )         
            .attr("x2", xScale(i) + xScale.bandwidth()/2 )  
            .attr("y1", config.height/2 + 9 )       
            .attr("y2", config.height/2 - 9 ) 
            .style("stroke-width", 10)
            .style("stroke", function(d) {
                if ( d === "W" ) {
                    f = chump.colours.green
                } else if ( d === "L" ) {
                    f = chump.colours.pink
                } else if ( d === "D" ) {
                    f = chump.colours.light_blue
                } else {
                    f = "Black"
                }

                return f
            })       


        })

    })


}


function build_fixtures(gw) {

    //define gameweek
    if (!(gw)) {
        gw = 30
    }

    gameweek = return_gameweek_string(gw)

    //build title block
    var title_container = d3.select("#title-block")
    .append("div")
    .classed("title-wrapper", true)
    .append("div")
    .classed("title-container", true)

    var title = title_container.append("div")
    .classed("text display large", true)
    .text("Fixtures")

    var subtitle = title_container.append("div")
    .classed("text display regular", true)
    .text("GW" + gw)

    //build logo
    logo = d3.select("#logo")
    .append("div")
    .classed("logo-wrapper", true)
    .append("div")
    .classed("logo-container", true)


    //build dataset
    dataset = []

    $.each( database["fixture_list"][gameweek], function(k, v) {
        temp_obj = {}
        temp_obj.home = v.H.manager_code    // update
        temp_obj.away = v.A.manager_code    // update

        dataset.push(temp_obj)

    } )

    //build content
    var viz_container = d3.select("#content-block")
    .append("div")
    .classed("fixture-list-wrapper", true)
    .append("div")
    .classed("fixture-list-container", true)

    var fixtures = viz_container.selectAll("div.fixture-wrapper")
    .data(dataset).enter()
    .append("div")
    .classed("fixture-wrapper", true)
    .append("div")
    .classed("fixture-container", true)
    .each( function(d, i){

        d3.select(this)
        .append("div")
        .classed("home team text display regular", true)
        .text(db_return_team_name(database, d.home))

        d3.select(this)
        .append("div")
        .classed("vs-block text display regular", true)
        .text("v")
        .style("background-color", function(d) {
            console.log(i)
            console.log(dataset.length)

            c = [chump.colours.green, chump.colours.light_blue, chump.colours.blue, chump.colours.purple, chump.colours.pink]

            return c[Math.ceil((c.length/dataset.length)*(i+1)-1)]
        })

        
        d3.select(this)
        .append("div")
        .classed("away team text display regular", true)
        .text(db_return_team_name(database, d.away))


    })

}

function build_results(gw) {

    //define gameweek
    if (!(gw)) {
        gw = 30
    }

    gameweek = return_gameweek_string(gw)

    //build title block
    var title_container = d3.select("#title-block")
    .append("div")
    .classed("title-wrapper", true)
    .append("div")
    .classed("title-container", true)

    var title = title_container.append("div")
    .classed("text display large", true)
    .text("Results")

    var subtitle = title_container.append("div")
    .classed("text display regular", true)
    .text("GW" + gw)

    dataset = []
    scores = []

    $.each( database["fixture_list"][gameweek], function(k, v) {
        temp_obj = {}
        temp_obj.home = v.H.manager_code    // update
        temp_obj.away = v.A.manager_code    // update

        //check for fixture scores, if fixture scores exist, fixture_played = true

        temp_obj.fixture_played = Boolean(db_return_fixture_score(database, v.H.manager_code, gameweek))

        //if fixture_played = true, add scores
        if (temp_obj.fixture_played) {
            temp_obj.home_score = db_return_fixture_score(database, temp_obj.home, gameweek)
            temp_obj.away_score = db_return_fixture_score(database, temp_obj.away, gameweek)

            temp_obj.home_result = db_return_fixture_result(database, temp_obj.home, gameweek)
            temp_obj.away_result = db_return_fixture_result(database, temp_obj.away, gameweek)

        }

        scores.push(temp_obj.home_score)
        scores.push(temp_obj.away_score)

        dataset.push(temp_obj)

    } )


    //build content
    var viz_container = d3.select("#content-block")
    .append("div")
    .classed("result-list-wrapper", true)
    .append("div")
    .classed("result-list-container", true)

    var fixtures = viz_container.selectAll("div.result-wrapper")
    .data(dataset).enter()
    .append("div")
    .classed("result-wrapper", true)
    .append("div")
    .classed("result-container text display regular", true)
    .each( function(d, i){

        var home_container = d3.select(this)
        .append("div")
        .classed("result-row home", true)
        .classed(d.home_result, true);

        var away_container = d3.select(this)
        .append("div")
        .classed("result-row away", true)
        .classed(d.away_result, true);

        d3.select(this).selectAll(".result-row")
        .each( function(d) {

            d3.select(this).append("div")
            .classed("indicator result-color", true)

            d3.select(this).append("div")
            .classed("team", true)

            d3.select(this).append("div")
            .classed("score result-color", true)

            d3.select(this).append("div")
            .classed("viz", true)

        })

        d3.select(this).selectAll(".result-row.home .team")
        .text(db_return_team_name(database, d.home))

        d3.select(this).selectAll(".result-row.away .team")
        .text(db_return_team_name(database, d.away))

        d3.select(this).selectAll(".result-row.home .score")
        .text(d.home_score)
        .append("span")
        .classed("rank text small", true)
        .text(function(d) {
            i = scores.sort(d3.descending).indexOf(d.home_score)
            s = "("+(i+1)+")"

            return s
        })

        d3.select(this).selectAll(".result-row.away .score")
        .text(d.away_score)
        .append("span")
        .classed("rank text small", true)
        .text(function(d) {
            i = scores.sort(d3.descending).indexOf(d.away_score)
            s = "("+(i+1)+")"

            return s
        })

        d3.select(this).selectAll(".result-row").each( function(d) {

            h = $(this).hasClass("home")

            viz_container =  d3.select(this).select(".viz")

            config = {
                "width": $(this).find(".viz").width(),
                "height": $(this).find(".viz").height()
            }

            svg = viz_container.append("svg")
            .attr("height", config.height)
            .attr("width", config.width)

            if (d3.min(scores) < 0) {
                xDomain = d3.extent(scores)
            } else {
                xDomain = [0, d3.max(scores)]
            }

            

            xScale = d3.scaleLinear()
            .domain(xDomain)
            .range([0, config.width])

            data = svg.append("rect")
            .attr("width", function(d) {

                if (h) {
                    a = d.home_score
                } else {
                    a = d.away_score
                }

                return xScale(a)

            } )
            .attr("height", config.height )

        })
    })

    var footnote = d3.select("#content-block")
    .append("div")
    .classed("footnote text small", true)
    .text("Figures in brackets indicate fixture score rank in GW"+gw)

}
