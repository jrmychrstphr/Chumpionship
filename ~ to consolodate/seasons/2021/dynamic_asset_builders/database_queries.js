function db_return_manager_fullname(input_database, manager_code) {
    a = input_database.player_data[manager_code].manager_info.manager_fullname
    return a
}

function db_return_team_name(input_database, manager_code) {
    a = input_database.player_data[manager_code].manager_info.team_name
    return a
}

function db_return_fixture_score(input_database, manager_code, gameweek) {
	o = input_database.player_data[manager_code].gw_performance
	k = return_gameweek_string(gameweek).toString()
	if (!(k in o)) { s = false } else { s = o[k].fixture_score }
    return s
}

function db_return_fixture_result(input_database, manager_code, gameweek) {
	o = input_database.player_data[manager_code].gw_performance
	k = return_gameweek_string(gameweek).toString()
	if (!(k in o)) { s = false } else { 
		if (o[k].fixture_result.toUpperCase() === "W") { s = "win" } else if (o[k].fixture_result.toUpperCase() === "L") { s = "loss" } else if (o[k].fixture_result.toUpperCase() === "D") { s = "draw" } 
	}
    return s
}