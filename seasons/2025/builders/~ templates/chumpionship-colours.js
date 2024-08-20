  <script>
   chump = {
		"colours": {
			"green": d3.rgb("rgb(0,219,113)"),
			"light_blue": d3.rgb("rgb(0,165,255)"),
			"blue": d3.rgb("rgb(0,78,250)"),
			"purple": d3.rgb("rgb(103,42,225)"),
			"pink": d3.rgb("rgb(255,41,176)"),
			"midnight_blue": d3.rgb("rgb(13,0,77)"),
			"light_midnight_blue": d3.rgb("rgb(22,0,122)"),
			"axis_lines": d3.rgb("rgb(90,90,115)"),
		},
		"gradients": {
			"css": {
			}
		}
	};

	chump.gradients.css.pink_blue_green = "linear-gradient(90deg, "+ chump.colours.pink +" 0%, "+ chump.colours.purple +" 25%, "+ chump.colours.blue +" 50%, "+ chump.colours.light_blue +" 75%, "+ chump.colours.green +" 100%)";
	chump.gradients.css.blue_green = "linear-gradient(90deg, "+ chump.colours.blue +" 0%, "+ chump.colours.light_blue +" 50%,"+ chump.colours.green +" 100%)";
	chump.gradients.css.pink_blue = "linear-gradient(90deg, "+ chump.colours.pink +" 0%, "+ chump.colours.purple +" 50%,"+ chump.colours.blue +" 100%)";
  </script>
