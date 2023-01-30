chump = {};
chump.colours = {};

chump.colours.green = d3.rgb("rgb(0,255,130)");
chump.colours.light_blue = d3.rgb("rgb(0,210,255)");
chump.colours.blue = d3.rgb("rgb(0,120,250)");
chump.colours.purple = d3.rgb("rgb(130,80,230)");
chump.colours.pink = d3.rgb("rgb(255,50,180)");
chump.colours.midnight_blue = d3.rgb("rgb(10,10,50)");
chump.colours.axis_lines = d3.rgb("rgb(90,90,115)");

chump.gradients = {};
chump.gradients.css = {};
chump.gradients.svg = {};

chump.gradients.css.pink_blue_green = "linear-gradient(90deg, "+ chump.colours.pink +" 0%, "+ chump.colours.purple +" 25%, "+ chump.colours.blue +" 50%, "+ chump.colours.light_blue +" 75%, "+ chump.colours.green +" 100%)"

chump.gradients.css.blue_green = "linear-gradient(90deg, "+ chump.colours.blue +" 0%, "+ chump.colours.light_blue +" 50%,"+ chump.colours.green +" 100%)"
chump.gradients.css.pink_blue = "linear-gradient(90deg, "+ chump.colours.pink +" 0%, "+ chump.colours.purple +" 50%,"+ chump.colours.blue +" 100%)"

chump.svg = {}
chump.svg.arrow = '<svg viewBox="0 0 100 100"><path d="M96.6,92.2c-2.6,2.6-6.6,3.1-9.7,1.3L56.3,76H43.7L13.1,93.5c-1.3,0.7-2.6,1.1-4,1.1c-2.1,0-4.2-0.8-5.7-2.3c-2.6-2.6-3.2-6.6-1.4-9.7L42.9,9.6C44.3,7,47,5.5,50,5.5c2.9,0,5.6,1.6,7,4.1l40.9,72.9C99.8,85.6,99.2,89.6,96.6,92.2z"/></svg>'