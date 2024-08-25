#' Creat a faceplot for a group.
#'
#' This function will create plots for a selected group from a timeseries. 
#'
#' @param filtered_power_consum time-series.
#' @param group_name Character, the column you want to group by.
#' @param file_name Character, the name of the file you want to save.
#' @param colors Dictionary, define your own color for a specific group.
#' @param colors Dictionary, define your own color for a specific group.

#' @return None
#'
#' @examples
#' \dontrun{
#' local_name_colors <- c(
#' "Christi Himmelfahrt" = "#E69F00", 
#' "Erster Weihnachtstag" = "#E69F00",  
#' "Karfreitag" = "#E69F00", 
#' "Neujahr" = "#E69F00",
#' "Ostermontag" = "#E69F00",
#' "Pfingstmontag" = "#E69F00",
#' "Reformationstag" = "#E69F00",
#' "Tag der Arbeit" = "#E69F00",
#' "Tag der Deutschen Einheit" = "#E69F00",
#' "Zweiter Weihnachtstag" = "#E69F00",
#' "Working-Day" = "darkgrey"
#' )
#' 
#' week_colors <- c(
#'   "Mo" = "darkgrey",
#'   "Di" = "darkgrey",
#'   "Mi" = "darkgrey",
#'   "Do" = "darkgrey",
#'   "Fr" = "darkgrey",
#'   "Sa" = "#E69F00",
#'   "So" = "#E69F00"
#' )
#' 
#' plot_by_group(filtered_power_consum, 
#'               group_name = "localName",
#'               file_name = "test.png",
#'               colors = local_name_colors,
#'               title = "Arbeitstage"
#'               )
#'
#'plot_by_group(filtered_power_consum, 
#'              group_name = "Wochentag",
#'              file_name = "test2.png",
#'              colors = week_colors,
#'              title = "Wochentage")
#'}

# Call the function

#' 
#'
#' @note -

plot_by_group <- function(filtered_power_consum, group_name, file_name, colors, title, y,
                          x_label, y_label) {
  
  agg_df <- aggregate(filtered_power_consum[[y]], 
                      by=list(filtered_power_consum[[group_name]]),
                      FUN=mean)
  
  names(agg_df) <- c(group_name, "GridLoadMean")
  max_value <- max(filtered_power_consum[[y]])
  
  p <-
    ggplot(filtered_power_consum, aes(x = Year, y = !!sym(y), fill = !!sym(group_name))) +
    geom_boxplot() + 
    geom_text(
      data = agg_df,
      aes(x = Inf, y = max_value*1.05, label = paste0("Durchschnitt: ", sprintf("%.2f", GridLoadMean)) ),
      color = "darkred",
      size = 3.5,
      hjust = 1.1, 
      vjust = 0.5
    ) +
    facet_wrap(as.formula(paste("~", group_name))) + 
    scale_fill_manual(values = colors) +  
    theme(
      legend.position = "none", 
      strip.text = element_text(size = 12) 
    ) +
    labs(
      title = title,
      x = x_label,
      y = y_label
    )
  
  ggsave(file_name, plot = p, width = 20, height = 10, dpi = 300)
}