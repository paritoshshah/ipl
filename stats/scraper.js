function fetch(url, callback) {
	var page = require('webpage').create();
	page.open(url, function(status) {
		if ( status === 'fail') {
			console.log('failed to open ' + url);
			phantom.exit();
		} else {
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

function scrape_batting_stats(page) {
	return page.evaluate(function() {
		var batting_stats = [];
		$('#inningsBat1 > tbody .inningsRow, #inningsBat2 > tbody .inningsRow').each(function() {
			var player = $('a', this);
			if (player.length == 0) return;
			var player_id = player.attr("href").split('/').pop().replace(/\..*/g, '');
			var player_data = $(this).text().trim().replace(/ /g,'').split('\n');
			var runs = player_data[2], balls = player_data[4], sixes = player_data[6];
			batting_stats.push([player_id, runs, balls, sixes]);
		});
		return batting_stats;
	});
}
//
//function scrape_bowling_points(page) {
//	return page.evaluate(function() {
//		var player_points = [];
//		$('#inningsBowl1 > tbody .inningsRow, #inningsBowl2 > tbody .inningsRow').each(function() {
//			var player = $('a', this);
//			if (player.length == 0) return;
//			var player_id = player.attr("href").split('/').pop().replace(/\..*/g, '');
//			var player_data = $(this).text().trim().replace(/ /g,'').split('\n');
//			var o = player_data[1], maidens = player_data[2], runs = player_data[3], wickets = player_data[4];
//			var overs = o.split(".");
//			overs.push(0);
//			var balls = overs[0] * 6 + overs[1];
//
//			var impact = runs === 0 ? -5 : 2 * sixes;
//			var points = 20 * wickets + balls * 1.5 - runs + 10 * runs / 25 + impact;
//
//			player_points.push([player_id, points])
//		});
//		return player_points;
//	});
//}
//

//url = 'http://stats.espncricinfo.com/indian-premier-league-2013/engine/records/team/match_results.html?id=2013;trophy=117;type=season';
//fetch(url, function(page) { console.log(scrape_list_of_matches(page)); phantom.exit(); });

url = 'http://www.espncricinfo.com/indian-premier-league-2013/engine/match/597998.html';
fetch(url, function(page) {
	stats = scrape_batting_stats(page);
	for(i=0; i<stats.length; i++) console.log(stats[i]); 
	phantom.exit(); 
});
