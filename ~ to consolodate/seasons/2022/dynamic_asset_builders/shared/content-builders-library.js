build = {

    table : function(gw) {

        // add this to database
        league_config = {}; league_config.prizes = 4; league_config.relegation = 3;

        //define gameweek
        if (!(gw)) { gw = 1 }

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

        //data
        dataset = []

        $.each( database.player_data, function(k, v) {

            temp_obj = {}

            temp_obj.manager_code = k
            temp_obj.position = parseInt(v.season_performance.league_position_array[parseInt(gw)-1])

            if (parseInt(gw) === 1) {
                temp_obj.change = 0
            } else {
                temp_obj.change = parseInt(v.season_performance.league_position_array[parseInt(gw)-1]) - parseInt(v.season_performance.league_position_array[parseInt(gw)-2])
            }

            temp_obj.score = v.season_performance.fixture_score_running_total_array[gw-1];
            temp_obj.league_points = v.season_performance.league_points_running_total_array[gw-1];

            temp_obj.streak = {};

            temp_obj.streak.results = v.season_performance.fixture_result_array.slice(0,(gw)).reverse();
            temp_obj.streak.len = 0;

            //console.log(temp_obj.streak.results)
            //console.log(temp_obj.streak.results[0])

            temp_obj.streak.type = temp_obj.streak.results[0]
            //console.log(temp_obj.streak.type)




            $.each(temp_obj.streak.results, function(idx, val) {
                if (val != temp_obj.streak.type) { return false; }
                temp_obj.streak.len++;
            })


            dataset.push(temp_obj)


        })

        dataset = dataset.slice().sort((a, b) => d3.descending(a.league_points, b.league_points) || d3.descending(a.score, b.score))


        console.log(dataset)


        //build content
        var viz_container = d3.select("#content-block")
        .append("div")
        .classed("league-table-wrapper", true)
        .append("div")
        .classed("league-table-container", true)

        let table_header = viz_container.append("div")
        .classed("table-header-wrapper", true)
        .append("div")
        .classed("table-header-container", true)

        table_header.append("div").classed("table-column position text small", true)
        .text("Pos.")

        table_header.append("div").classed("table-column team-name text small", true)
        .text("Team / Manager")
        
        table_header.append("div").classed("table-column score text small", true)
        .text("Score")
        
        table_header.append("div").classed("table-column league-points text small", true)
        .text("Points")
        
        table_header.append("div").classed("table-column viz text small", true)
        .text("Streak")
        


        var table_rows = viz_container.selectAll("div.table-row-wrapper")
        .data(dataset).enter()
        .append("div")
        .classed("table-row-wrapper", true)
        .append("div")
        .classed("table-row-container", true)
        .each( function(d, i) {

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
            .append("span")
            .classed("rank text small", true)
            .text(db_return_manager_fullname(database, d.manager_code))
            
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

            var viz_container = d3.select(this)
            .append("div")
            .classed("table-column viz", true)

            config = {
                "width": $(this).find(".viz").width(),
                "height": $(this).find(".viz").height(), 
                "padding": {
                    "top": 0,
                    "right": 0,
                    "bottom": 0,
                    "left": 5
                },
                "circle": {
                    "radius": 10,
                    "stroke_width": 2
                }
            }

            svg = viz_container.append("svg")
            .attr("height", config.height)
            .attr("width", config.width)
            .attr("viewBox","0 0 " + config.width + " " + config.height)

            // define max streak length
            var xMax = function() {
                a  = []
                $.each( dataset, function(idx, val) {
                    a.push(val.streak.len)
                })
                a = d3.max(a)
                return a
            } ()

            let colour;

            if (d.streak.type === "w") {
                colour = chump.colours.green
            } else if (d.streak.type === "l") {
                colour = chump.colours.pink
            } else if (d.streak.type === "d") {
                colour = chump.colours.light_blue
            } else {
                colour = "white"
            }

            // add data
            var data_group = svg.append("g").classed("data-goup", true)

            //calculate spacing
            let s = function(){

                let s, t = 35, r = config.circle.radius; // t = gap for text

                //calculate how much space is available for circles
                let gap = (config.width - (config.padding.left + config.padding.right) - (t+r));

                if (gap/xMax > r) {
                    s = r;
                } else {
                    s = gap/xMax                    
                }

                return s;

            } ()

            for (ii = 0; ii < d.streak.len; ii++) {
                console.log(d.streak)
                data_group.append("circle")
                .attr("cx", config.circle.radius+(ii*s) + config.padding.left)
                .attr("cy", config.height/2)
                .attr("r", config.circle.radius)
                .attr("stroke-width", config.circle.stroke_width)
                .style("stroke", chump.colours.midnight_blue)
                .style("fill", colour)
            }

            let text = data_group.append("text")
            .classed("text small bold", true)
            .attr("x", config.circle.radius + (ii*s) + config.padding.left + 5)
            .attr("y", config.height/2)
            .attr("dy", 5.5)
            .style("text-anchor", "start")
            .style("fill", colour)
            .text(function(d) {
                let msg;

                msg = d.streak.type + d.streak.len;

                return msg.toUpperCase();
            })

        })
    },

        fixtures : function(gw) {

        //define gameweek
        if (!(gw)) { gw = 1 }

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
            temp_obj.home = v.home_team    // update
            temp_obj.away = v.away_team    // update

            temp_obj.home_rank = database["player_data"][v.home_team]["season_performance"]["league_position_array"][gw-2]
            temp_obj.away_rank = database["player_data"][v.away_team]["season_performance"]["league_position_array"][gw-2]

            dataset.push(temp_obj)

        } )

        dataset.sort((a,b) => (db_return_team_name(database, a.home) > db_return_team_name(database, b.home)));

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

            let home = d3.select(this)
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

            
            let away = d3.select(this)
            .append("div")
            .classed("away team text display regular", true)
            .text(db_return_team_name(database, d.away))

            if ( d.home_rank && d.away_rank ) {

                home.append("span")
                .classed("rank text small", true)
                .text("("+d.home_rank+")")

                away.append("span")
                .classed("rank text small", true)
                .text("("+d.away_rank+")")
                
            }

        })

        if ( gw > 1 ) {

            var footnote = d3.select("#content-block")
            .append("div")
            .classed("footnote text small", true)
            .text("Figures in brackets indicate league rank ahead of GW"+gw)

        }

    },

    results : function(gw) {

        //define gameweek
        if (!(gw)) {
            gw = 1
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
            temp_obj.home = v.home_team    // update
            temp_obj.away = v.away_team    // update

            //check for fixture scores, if fixture scores exist, fixture_played = true

            temp_obj.fixture_played = Boolean(db_return_fixture_score(database, v.home_team, gameweek))

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

        dataset.sort((a,b) => (db_return_team_name(database, a.home) > db_return_team_name(database, b.home)));


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

            let result_row = d3.select(this)
            .append("div")
            .classed("result-row", true)

            result_row.append("div")
            .classed("indicator result-color", true)
            .classed(d.home_result, true)

            let home_team = result_row.append("div")
            .classed("home team", true)
            .text(db_return_team_name(database, d.home))

            let home_score = result_row.append("div")
            .classed("home score result-color", true)
            .classed(d.home_result, true)

            let away_score = result_row.append("div")
            .classed("away score result-color", true)
            .classed(d.away_result, true)

            let away_team = result_row.append("div")
            .classed("away team", true)
            .text(db_return_team_name(database, d.away))

            result_row.append("div")
            .classed("indicator result-color", true)
            .classed(d.away_result, true)


            home_score.text(d.home_score)
            .append("span")
            .classed("rank text small", true)
            .text(function(d) {
                i = scores.sort(d3.descending).indexOf(d.home_score)
                s = "("+(i+1)+")"

                return s
            })


            away_score.text(d.away_score)
            .append("span")
            .classed("rank text small", true)
            .text(function(d) {
                i = scores.sort(d3.descending).indexOf(d.away_score)
                s = "("+(i+1)+")"

                return s
            })

            /*

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

            */
        })

        var footnote = d3.select("#content-block")
        .append("div")
        .classed("footnote text small", true)
        .text("Figures in brackets indicate fixture score rank in GW"+gw)

    }
}
