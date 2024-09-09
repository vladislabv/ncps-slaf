#' Creat a faceplot for a group.
#'
#' This function will create plots for a selected group from a timeseries. 
#'
#' @param filtered_power_consum time-series.
#' @param group_name Character, the column you want to group by.
#' @param file_name Character, the name of the file you want to save.
#' @param colors Dictionary, define your own color for a specific group.
#' @param title Title of the Plot
#' @param y Y-Values
#' @param x_label Label of X
#' @param y_label Label of Y
#' 


plot_by_group <- function(filtered_power_consum, group_name, file_name, colors, title, y,
                          x_label, y_label) {
  
  filtered_power_consum <- filtered_power_consum |>
    mutate(Group = as.factor(!!sym(group_name)))
  
  agg_df <- aggregate(filtered_power_consum[[y]], 
                      by=list(filtered_power_consum$Group),
                      FUN=mean)
  
  names(agg_df) <- c("Group", "GridLoadMean")
  max_value <- max(filtered_power_consum[[y]])
  
  p <-
    ggplot(filtered_power_consum, aes(x = Year, y = !!sym(y), fill = Group)) +
    geom_boxplot() + 
    geom_text(
      data = agg_df,
      aes(x = Inf, y = max_value*1.05, label = paste0("Durchschnitt: ", sprintf("%.2f", GridLoadMean)) ),
      color = "darkred",
      size = 3.5,
      hjust = 1.1, 
      vjust = 0.5
    ) +
    facet_wrap(as.formula(paste("~", "Group"))) + 
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