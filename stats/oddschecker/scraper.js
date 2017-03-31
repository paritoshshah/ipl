var system = require('system');
var args = system.args;

if (args.length < 2) {
	console.log('Usage: phantomjs scraper.js [type]');
	console.log('Where [type] is either batsman or bowler');
	phantom.exit();
}

function fetch(url, callback) {
	var page = require('webpage').create();
	page.open(url, function(status) {
		if ( status === 'fail') {
			console.log('failed to open ' + url);
			phantom.exit();
		} else {
			console.log('scraping ' + url);
			callback(page);
		}
	});
}

var fs = require('fs');
function scrape_odds(url, outputFile) {
	fetch(url, function(page) {
		odds = page.evaluate(function() {
			return $.map($('#t1 > tr'), function(player) { return $(player).attr("data-bname") + "," + (1/$(player).attr("data-best-dig")).toFixed(3); });
		});

		console.log('generating ' + outputFile);
		try {
			fs.write(outputFile, odds.join('\n'), 'w');
		}
		catch(e) {
			console.log(e);
		}

		page.close();
		phantom.exit();
	});
}

function scrape_mom_odds(urls) {
	if(urls.length == 0) {
		phantom.exit();
		return;
	}

	url = urls.pop();
	fetch(url, function(page) {
		mom_odds = page.evaluate(function() {
			return $.map($('#t1 > tr'), function(player) { 
				name = $(player).attr("data-bname");

				// reformat names of type "lastname, firstname" -> "firstname lastname"
				parts = name.split(", ");
				if (parts.length > 1) {
					name = parts[1] + " " + parts[0];
				}

				return  name + "," + (1/$(player).attr("data-best-dig")).toFixed(3); 
			});
		});

		console.log('generating mom_odds.csv');
		try {
			fs.write('mom_odds.csv', mom_odds.join('\n') + '\n', 'a');
		}
		catch(e) {
			console.log(e);
		}
		page.close();
		scrape_mom_odds(urls);
	});
}

urls = [
	'http://www.oddschecker.com/cricket/indian-premier-league/mumbai-indians-v-rising-pune-supergiants/man-of-the-match',
	'http://www.oddschecker.com/cricket/indian-premier-league/kolkata-knight-riders-v-delhi-daredevils/man-of-the-match',
	'http://www.oddschecker.com/cricket/indian-premier-league/kings-xi-punjab-v-gujarat-lions/man-of-the-match',
	'http://www.oddschecker.com/cricket/indian-premier-league/royal-challengers-bangalore-v-hyderabad-sunrisers/man-of-the-match'
];

//scrape_mom_odds(urls);
url = 'https://www.oddschecker.com/cricket/ipl/indian-premier-league/top-tournament-' + args[1];
scrape_odds(url, args[1] + '_odds_oc.csv');
