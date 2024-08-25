

plot_year_month_week_day <- function(df, date_column, y, 
                                     from_year, to_year,
                                     from_week, to_week, year_for_week, 
                                     from_day, to_day, month_for_day,  year_for_day, 
                                     from_month, to_month, year_for_month,
                                     holiday, day_of_week
                                     ){
  df <- df |>
    mutate(
      date_to_filter = !!sym(date_column),
      Month = as.factor(month(date_to_filter)),
      Year = as.factor(year(date_to_filter)),
      Day = as.factor(day(date_to_filter)),
      DayWithWeek = paste0(as.factor(day(date_to_filter)), as.character(!!sym(day_of_week))),
      Week = as.factor(week(date_to_filter))
    )
  
  df_year <- df |>
    filter(year(date_to_filter) >= from_year & year(date_to_filter) <= to_year)
  
  df_month <- df |>
    filter(year(date_to_filter) == year_for_month) |>
    filter(month(date_to_filter) >= from_month & month(date_to_filter) <= to_month)
  
  df_week <- df |>
    filter(year(date_to_filter) == year_for_week) |>
    filter(week(date_to_filter) >= from_week & week(date_to_filter) <= to_week)
  
  df_day <- df |>
    filter(year(date_to_filter) == year_for_day) |>
    filter(month(date_to_filter) == month_for_day) |>
    filter(day(date_to_filter) >= from_day & day(date_to_filter) <= to_day) |>
    arrange(Day)

  day_order <- unique(df_day$DayWithWeek)
  
  
  year_plot <- ggplot(data = df_year, aes(x = date_to_filter, y = !!sym(y), color=!!sym(holiday))) +
    geom_path(aes(group = 1)) +
    scale_color_manual(values = c("FALSE" = "black", "TRUE" = "darkred"),
                       labels = c("FALSE" = "Normal Day", "TRUE" = "Holiday")) +
    scale_x_datetime(
      date_minor_breaks = "1 month", date_breaks = "2 months",
      date_labels = "%b") +
    facet_wrap(~ Year, scales = "free_x") +
    labs(
      x = "Months",  
      y = "Grid Load",     
      title = "Yearly Grid Load 2015-2023"  
    )
  ggsave("plots\\raw_years.png", plot = year_plot, width = 20, height = 10, dpi = 300)
  
  month_plot <- ggplot(data=df_month, aes(x=date_to_filter, y=!!sym(y), color=!!sym(holiday))) +
    geom_path(aes(group = 1)) +
    scale_color_manual(values = c("FALSE" = "black", "TRUE" = "red")) +
    facet_wrap(~ Month, scales = "free_x")+
    labs(
      x = "Days",  
      y = "Date Load",     
      title = "Monthly representation of Grid Load 2018"  
    )
  ggsave("plots\\raw_month.png", plot = month_plot, width = 20, height = 10, dpi = 300)
  
  week_plot <- ggplot(data=df_week, aes(x=date_to_filter, y=!!sym(y), color=!!sym(holiday))) +
    geom_path(aes(group = 1)) +
    scale_color_manual(values = c("FALSE" = "black", "TRUE" = "red")) +
    facet_wrap(~ Week, scales = "free_x")+
    scale_x_datetime(
      date_minor_breaks = "1 day", date_breaks = "1 day",
      date_labels = "%a") +
    labs(
      x = "Day of Week",  
      y = "Grid Load",
      title = "Weekly representation of Grid Load for 2018"  
    )
  ggsave("plots\\raw_week.png", plot = week_plot, width = 20, height = 10, dpi = 300)
  
  day_plot <- ggplot(data=df_day, aes(x=date_to_filter, y=!!sym(y), color=!!sym(holiday))) +
    geom_path(aes(group = 1)) +
    scale_color_manual(values = c("FALSE" = "black", "TRUE" = "red")) + 
    facet_wrap(~ factor(DayWithWeek, levels=day_order), scales = "free_x", ncol=7) +
    scale_x_datetime(
      date_minor_breaks = "1 hour", date_breaks = "4 hours",
      date_labels = "%H") +
    labs(
      x = "Hours",  
      y = "Grid Load",
      title = "Daily representation of Grid Load for Apr. 2018"  
    )
  ggsave("plots\\raw_day.png", plot = day_plot, width = 20, height = 10, dpi = 300)

}