
-- sqlite doesn't support outer joins, so if you have to do (2014 outer join 2015), you actually need to do (2014 left join 2015 union all 2015 left join 2014 where 2014.firstname is null)
-- the query below was used to stich together 2014, 2015, 2016 stats and generate player_stats_14_15_16.csv
select l.firstname, num_games_2014, avg_points_2014, num_games_2015, avg_points_2015, r.num_games as num_games_2016, r.avg_points as avg_points_2016 from (select l.firstname, l.num_games as num_games_2014, l.avg_points as avg_points_2014, m.num_games as num_games_2015, m.avg_points as avg_points_2015 from player_stats_2014 l left outer join player_stats_2015 m on l.firstname = m.firstname union all select m.firstname, l.num_games as num_games_2014, l.avg_points as avg_points_2014, m.num_games as num_games_2015, m.avg_points as avg_points_2015 from player_stats_2015 m left join player_stats_2014 l on m.firstname = l.firstname where l.firstname is null) l left join player_stats_2016 r on l.firstname = r.firstname;

-- 14_cum
create table player_stats_14_cum as select l.firstname, l.num_games as num_games_2013, l.avg_points as avg_points_2013, m.num_games as num_games_2014, m.avg_points as avg_points_2014 from player_stats_2013 l left outer join player_stats_2014 m on l.firstname = m.firstname union all select m.firstname, l.num_games as num_games_2013, l.avg_points as avg_points_2013, m.num_games as num_games_2014, m.avg_points as avg_points_2014 from player_stats_2014 m left join player_stats_2013 l on m.firstname = l.firstname where l.firstname is null;

-- 15_cum
create table player_stats_15_cum as select l.*, m.num_games as num_games_2015, m.avg_points as avg_points_2015 from player_stats_14_cum l left outer join player_stats_2015 m on l.firstname = m.firstname union all select m.firstname, num_games_2013, avg_points_2013, num_games_2014, avg_points_2014, m.num_games as num_games_2015, m.avg_points as avg_points_2015 from player_stats_2015 m left join player_stats_14_cum l on m.firstname = l.firstname where l.firstname is null;

-- player_stats_2016
create table player_stats_2016wc as select firstname, count(*) as num_games, sum(fanta_points)/count(*) as avg_points from player_stats_2016_raw group by firstname;
update player_stats_2016wc set firstname='Christopher Morris' where firstname = 'Chris Morris';
update player_stats_2016wc set firstname='Francois du Plessis' where firstname = 'Faf du Plessis';
update player_stats_2016wc set firstname='Steve Smith' where firstname = 'Steven Smith';

-- 16wc_cum
create table player_stats_16wc_cum as select l.*, m.num_games as num_games_2016wc, m.avg_points as avg_points_2016wc from player_stats_15_cum l left outer join player_stats_2016wc m on l.firstname = m.firstname union all select m.firstname, num_games_2013, avg_points_2013, num_games_2014, avg_points_2014, num_games_2015, avg_points_2015, m.num_games as num_games_2016wc, m.avg_points as avg_points_2016wc from player_stats_2016wc m left join player_stats_15_cum l on m.firstname = l.firstname where l.firstname is null;

-- 2016 pre-ipl stats
select l.*, r.* from squads_2016 l left join player_stats_16wc_cum r on l.firstname = r.firstname;
select l.*, r.* from squads_2016 l left join batting_odds_2016 r on l.firstname = r.firstname;
