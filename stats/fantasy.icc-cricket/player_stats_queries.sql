
-- sqlite doesn't support outer joins, so if you have to do (2014 outer join 2015), you actually need to do (2014 left join 2015 union all 2015 left join 2014 where 2014.firstname is null)
-- the query below was used to stich together 2014, 2015, 2016 stats and generate player_stats_14_15_16.csv
select l.firstname, num_games_2014, avg_points_2014, num_games_2015, avg_points_2015, r.num_games as num_games_2016, r.avg_points as avg_points_2016 from (select l.firstname, l.num_games as num_games_2014, l.avg_points as avg_points_2014, m.num_games as num_games_2015, m.avg_points as avg_points_2015 from player_stats_2014 l left outer join player_stats_2015 m on l.firstname = m.firstname union all select m.firstname, l.num_games as num_games_2014, l.avg_points as avg_points_2014, m.num_games as num_games_2015, m.avg_points as avg_points_2015 from player_stats_2015 m left join player_stats_2014 l on m.firstname = l.firstname where l.firstname is null) l left join player_stats_2016 r on l.firstname = r.firstname;