#' Load German Holidays
#'
#' This function retrieves public holidays in Germany for a specified range of years 
#' using the Nager.Date API and returns a vector of unique dates that are recognized 
#' as public holidays.
#'
#' @param from_year Integer. The start year for which to retrieve holidays.
#' @param to_year Integer. The end year for which to retrieve holidays.
#'
#' @return A vector of `Date` objects representing public holidays in Germany, 
#' filtered to include only globally recognized holidays.
#'
#' @examples
#' \dontrun{
#' # Load holidays from 2015 to 2024
#' german_holidays <- load_german_holidays(2015, 2024)
#' }
#'
#' @note -
#' 
#' @importFrom httr GET content
#' @importFrom dplyr bind_rows mutate group_by slice ungroup filter
#' @export

load_german_holidays <- function(from_year, to_year, location) {
  all_holidays <- list()
  
  for (year in from_year:to_year) {
    hol <- httr::GET(paste0(
      "https://date.nager.at/api/v3/publicholidays/",
      year,
      location
    )) |>
      httr::content()
    
    holidays <- lapply(hol, `[`, c("date", "localName", "name", "fixed", "global")) |>
      bind_rows() |>
      mutate(date = as.Date(date))
    
    all_holidays[[as.character(year)]] <- hol
  }
  
  all_holidays_df <- bind_rows(all_holidays, .id = "index") |>
    group_by(date) |>
    slice(1) |>
    ungroup() |>
    filter(global == TRUE)
  
  
  return(all_holidays_df)
  
}