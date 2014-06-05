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

function scrape_list_of_matches(page) {
	return page.evaluate(function() {
		var urls = [];
		$('#ciHomeContentlhs table:nth-child(1) > tbody  a').each(function() { if (this.innerText === "T20") urls.push(this.href); });
		return urls;
	});
}

// output format: [id, name, runs, balls, sixes]
function scrape_batting_stats(page) {
	return page.evaluate(function() {
		var batting_stats = [];
		$('#inningsBat1 > tbody .inningsRow, #inningsBat2 > tbody .inningsRow').each(function() {
			var player = $('a', this);
			if (player.length == 0) return;
			var player_id = player.attr("href").split('/').pop().replace(/\..*/g, '');
			var name = player.text();
			var player_data = $(this).text().trim().replace(/ /g,'').split('\n');
			if (player_data.length < 7) {
				console.log("ERROR, insufficient data while scraping batting stats");
				return;
			}
			var runs = player_data[2], balls = player_data[4], sixes = player_data[6];
			batting_stats.push([player_id, name, runs, balls, sixes]);
		});
		return batting_stats;
	});
}

function scrape_bowling_stats(page) {
	return page.evaluate(function() {
		var bowling_stats = [];
		$('#inningsBowl1 > tbody .inningsRow, #inningsBowl2 > tbody .inningsRow').each(function() {
			var player = $('a', this);
			if (player.length == 0) return;
			var player_id = player.attr("href").split('/').pop().replace(/\..*/g, '');
			var name = player.text();
			var player_data = $(this).text().trim().replace(/ /g,'').split('\n');
			var o = player_data[1], maidens = player_data[2], runs = player_data[3], wickets = player_data[4];
			var overs = o.split(".");
			overs.push("0");
			var balls = parseInt(overs[0]) * 6 + parseInt(overs[1]);

			bowling_stats.push([player_id, name, wickets, balls, runs, maidens]);
		});
		return bowling_stats;
	});
}

function scrape_player_of_the_match(page) {
	return page.evaluate(function() {
		var player = "";
		$('.notesRow').each(function() {
			if($(this).text().indexOf("Player of the match") >= 0) {
				player = $(this).text().trim().split('\n')[1].split('(')[0].trim();
			}
		});

		return player;
	});
}

var fs = require('fs');
function process_match_stats(url, callback) {
	fetch(url, function(p) {
		match_id = url.split('/').pop().replace(/\..*/g, '');
		stats = scrape_batting_stats(p);
		for(j=0; j<stats.length; j++) {
			try {
				fs.write('raw/batting/' + match_id + '.csv', match_id + ',' + stats[j].join(',') + '\n', 'a')
			}
			catch(e) {
				console.log(e);
			}
		}

		stats = scrape_bowling_stats(p);
		for(j=0; j<stats.length; j++) {
			try {
				fs.write('raw/bowling/' + match_id + '.csv', match_id + ',' + stats[j].join(',') + '\n', 'a');
			}
			catch(e) {
				console.log(e);
			}
		}

		mvp = scrape_player_of_the_match(p);
		try {
			fs.write('raw/mvp/' + match_id + '.csv', match_id + ',' + mvp, 'a');
		}
		catch(e) {
			console.log(e);
		}

		p.close();
		callback.apply();
	});
}

function scrape_dots(page) {
	return page.evaluate(function() {
		dots_counter = {};

		$("p.commsText").each(function() {
			if ($(this).text().indexOf("no run") >= 0) {
				bowler = $(this).text().split('\n')[0].replace(/\ to.*/g, '');
				if (dots_counter[bowler] === undefined) dots_counter[bowler] = 0;
				dots_counter[bowler]++;
			}
		});

		return dots_counter;
	});
}

function process_innings_commentary_stats(url, innings, callback) {
	fetch(url + "?innings=" + innings + ";view=commentary", function(p) {
		match_id = url.split('/').pop().replace(/\..*/g, '');
		stats = scrape_dots(p);
		for ( b in stats ) {
			fs.write('raw/dots/' + match_id + '.csv', match_id + ',' + b + ',' + stats[b] + '\n', 'a');
		}

		p.close();
		callback.apply();
	});
}

var matches = [];
var match_idx = 0;
var innings = 1;
function process() {
	if ( match_idx < matches.length ) {
		process_innings_commentary_stats(matches[match_idx], innings, process);
		if (innings == 2) {
			innings = 1;
			match_idx++;
		}
		else {
			innings = 2;
		}
	}
	else {
		phantom.exit();
	}
}

url = 'http://stats.espncricinfo.com/indian-premier-league-2013/engine/records/team/match_results.html?id=2013;trophy=117;type=season';
fetch(url, function(page) { 
	matches = scrape_list_of_matches(page);
	process();
});

//url = 'http://www.espncricinfo.com/indian-premier-league-2013/engine/match/598066.html';
//fetch(url, function(page) {
//	stats = scrape_batting_stats(page);
//	for(i=0; i<stats.length; i++) console.log(stats[i]); 
//	phantom.exit(); 
//});

//fetch(url, function(page) { console.log(scrape_player_of_the_match(page)); phantom.exit(); });
//url = 'http://www.espncricinfo.com/indian-premier-league-2013/engine/match/598066.html?innings=1;view=commentary';
//fetch(url, function(page) { 
//	stats = scrape_dots(page);
//	for ( b in stats ) {
//		console.log(b + ',' + stats[b]);
//	}
//	phantom.exit(); 
//});

