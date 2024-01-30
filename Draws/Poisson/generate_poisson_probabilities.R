library (dplyr)
library (rlang)
library(stringi)


get_historical_data <- function (history_path, season1, season2, n_){

  # extract historic results
  history <- read.csv(history_path, stringsAsFactors = FALSE)
  teams <- unique(history$Home.Team)

  # get info from the 20xx up to present
  seasons <- sapply(season1:season2, function(x) paste0(2000+x, '-', x+1))
  seasons_ <- character()
  for (season in seasons){
    if (nchar(season) == 6){
      stri_sub(season, 6, 5) <- '0'
      seasons_ <- append(seasons_, season)
    }
    else{
      seasons_ <- append(seasons_, season)
    }
  }

  recent <- history %>%
    filter(Season %in% seasons_)

  ave_home <- recent %>%
    group_by(Home.Team) %>%
    summarize (ave_scored_h = mean(FTHG), ave_conceded_h = mean(FTAG)) %>%
    filter (Home.Team %in% teams) %>% rename(Team = Home.Team)

  ave_away <- recent %>%
    group_by(Away.Team) %>%
    summarize (ave_scored_a = mean(FTAG), ave_conceded_a = mean(FTHG)) %>%
    filter (Away.Team %in% teams)  %>% rename(Team = Away.Team)

  ave <- merge(ave_home, ave_away, by = 'Team')

  # more precise result with pairwise
  hist_pair <- recent %>%
    group_by(Home.Team, Away.Team) %>%
    filter (Home.Team %in% teams, Away.Team %in% teams) %>%
    summarize (match = n(), ave_home_scored = mean(FTHG), ave_away_scored = mean(FTAG))

  hist_pair <- hist_pair %>%
    filter(match == n_)

  rm(history, seasons_, ave_home, ave_away, recent)
  return(hist_pair)
}


get_score <- function (home, away, iterations, hist_pair){
  # hist_pair contains the summary of the pairing
  subset <- hist_pair[which(hist_pair$Home.Team == home & hist_pair$Away.Team == away), ]
  win <- 0
  loss <- 0
  draw <- 0

  h <- rpois(iterations, subset$ave_home_scored[1])
  a <- rpois(iterations, subset$ave_away_scored[1])

  if (is_na(h[1])) {
    return(c('-', '-', '-'))
  }

  for (i in seq_along(h)){
    if (h[i] > a[i]){
      win <- win + 1
    } else if (h[i] < a[i]){
      loss <- loss + 1
    } else{
      draw <- draw + 1
    }
  }

  H_win_perc <- win/iterations
  A_win_perc <- loss/iterations
  D_perc <- draw/iterations
  return(c(H_win_perc, A_win_perc, D_perc))
}


get_result_prediction <- function (p_home, p_away, p_draw){
  p_home_as_double <- as.double(p_home)
  p_away_as_double <- as.double(p_away)
  p_draw_as_double <- as.double(p_draw)
  home <- 0
  away <- 0
  draw <- 0
  if (abs(p_home_as_double - p_away_as_double) <= 0.01 | (p_draw_as_double > p_home_as_double & p_draw_as_double > p_away_as_double)){
    draw <- 1
  }
  else if (p_home_as_double > p_away_as_double & p_home_as_double > p_draw_as_double){
    home <- 1
  }
  else if (p_away_as_double > p_home_as_double & p_away_as_double > p_draw_as_double){
    away <- 1
  }
  return(c(away, draw, home))
}


make_matchday_predictions <- function (home_teams, away_teams, hist_pair, num_pred, predictions){
  options(warn=-1)
  p_home_new <- list()
  p_away_new <- list()
  p_draw_new <- list()
  for (i in seq_along(home_teams)){
    try( {
      pred <- get_score(home_teams[[i]], away_teams[[i]], 1000000, hist_pair)
      pred <- c(home_teams[[i]], away_teams[[i]], pred)

      if (num_pred == 1) {
        new_df <- data.frame(pred[[1]], pred[[2]], pred[[3]], pred[[4]], pred[[5]])
        names(new_df) <- c('Home Team', 'Away Team', 'P(Home) 1', 'P(Away) 1', 'P(Draw) 1')
        predictions <- rbind(predictions, new_df)
      }
      else{
        p_home_new <- c(p_home_new, pred[[3]])
        p_away_new <- c(p_away_new, pred[[4]])
        p_draw_new <- c(p_draw_new, pred[[5]])
      }
    }
    , silent = TRUE)
  }
  if (num_pred == 1){
    return (predictions)
  }
  else{
    p_home_new <- unlist(p_home_new)
    p_away_new <- unlist(p_away_new)
    p_draw_new <- unlist(p_draw_new)
    predictions$p1 <- p_home_new
    predictions$p2 <- p_away_new
    predictions$p3 <- p_draw_new
    names(predictions)[names(predictions) == 'p1'] <- paste('P(Home)', toString(num_pred), sep = ' ')
    names(predictions)[names(predictions) == 'p2'] <- paste('P(Away)', toString(num_pred), sep = ' ')
    names(predictions)[names(predictions) == 'p3'] <- paste('P(Draw)', toString(num_pred), sep = ' ')
    return (predictions)
  }
}


predictions <- function(x){

  # poiss_seasons <- c(6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)
  poiss_seasons <- c(8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)
  country <- c('England/')
  leagues <- c('EPL')
  for (league in leagues){
    path <- paste('/Users/dorianglon/Desktop/Project/data/', country, league, '/historical_df.csv', sep = '')
    dir_to_create <- paste('/Users/dorianglon/Desktop/Project/data/', country, league, '/poisson/', sep = '')

    if (!dir.exists(dir_to_create)) {dir.create(dir_to_create)}

    for (i in poiss_seasons){
      out_file <- paste('/Users/dorianglon/Desktop/Project/data/', country, league, '/poisson/poisson', toString(i), '_',
                        toString(i+1), '.csv', sep = '')
      df <- read.csv(path, stringsAsFactors = FALSE)
      s1 <- i

      seasons_ <- sapply(s1:s1, function(x) paste0(2000+x, '-', x+1))
      if (s1 < 9) {
        stri_sub(seasons_, 6, 5) <- '0'
      }
      recent <- df %>%
        filter(Season %in% seasons_)
      home_teams <- recent[[1]]
      away_teams <- recent[[2]]
      poisson1 <- s1-(x-1)
      num_pred <- 1
      predictions <- data.frame()
      n <- x
      for (var in poisson1:s1-1){
        season1 <- var
        season2 <- s1-1
        hist_pair <- get_historical_data(path, season1, season2, n)
        predictions <- make_matchday_predictions(home_teams, away_teams, hist_pair, num_pred, predictions)
        num_pred <- num_pred + 1
        n <- n - 1
      }
      write.csv(predictions, out_file)
    }
  }
}


predictions_new_data <- function(x){

  country <- c('England/')
  leagues <- c('EFL')
  for (league in leagues){
    path <- paste('/Users/dorianglon/Desktop/Steti Capital/data/', country, league, '/2023/historical_df.csv', sep = '')
    dir_to_create <- paste('/Users/dorianglon/Desktop/Steti Capital/data/', country, league, '/2023/poisson/', sep = '')
    historical <- paste('/Users/dorianglon/Desktop/Steti Capital/data/', country, league, '/historical_df.csv', sep = '')

    if (!dir.exists(dir_to_create)) {dir.create(dir_to_create)}

    out_file <- paste(dir_to_create, '2023poisson.csv')
    df <- read.csv(path, stringsAsFactors = FALSE)

    seasons_ <- '2022-23'
    recent <- df %>%
      filter(Season %in% seasons_)
    home_teams <- recent[[1]]
    away_teams <- recent[[2]]
    s1 <- 22
    poisson1 <- s1-(x - 1)
    num_pred <- 1
    predictions <- data.frame()
    n <- x
    for (var in poisson1:s1-1){
      season1 <- var
      season2 <- s1-1
      hist_pair <- get_historical_data(historical, season1, season2, n)
      predictions <- make_matchday_predictions(home_teams, away_teams, hist_pair, num_pred, predictions)
      num_pred <- num_pred + 1
      n <- n - 1
    }
    write.csv(predictions, out_file)
  }
}


predictions(3)
# predictions_new_data(x=1)

