def top_score_message(gw,d_players):
		score = max([x['fixture_score'] for x in d_players if x['gw'] == gw])
		results = [x for x in d_players if x['gw'] == gw and x['fixture_score'] == score]

		msg = f""

		if len(results) > 1:
			msg += f"{written_number(len(results)).title()} bosses topped the scoreboard in GW{int(gw)}: "

		for idx,x in enumerate(results):


			count = len([c for c in d_players if c['gw'] <= gw and c['manager_code'] == x['manager_code'] and c['fixture_score_rank'] == 1])

			msg += f"{x['manager_name']} topped the scoreboard"
			msg += f" for the {ord(int(count))} time this season"
			msg += f" with a haul of {int(x['fixture_score'])}"
			
			if len(results) > 1: 
				msg += f"; "
			else:
				msg += f"."

		szn_top = max([x['fixture_score'] for x in d_players if x['gw'] <= gw])
		prev = max([x['fixture_score'] for x in d_players if x['gw'] < gw])

		if score == szn_top:
			msg += f" This is a new season-high score."

		return msg