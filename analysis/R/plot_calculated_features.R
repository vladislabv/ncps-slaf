#' Will Plot two variables against each other as as geom_point plot.
#'
#' @param df your data
#' @param file_name Will be safed here
#' @param x X-Values
#' @param y Y-Values
#' @param x_label Label for x-axis
#' @param y_label Label for y-axis
#'

plot_calculated_features <- function(df, file_name, x, y, x_label, y_label){

  p <- ggplot(df |> mutate(WorkDay = as.factor(WorkDay)), 
              aes(x=!!sym(x), y=!!sym(y), color=WorkDay)) +
    geom_point(alpha=0.5, size=0.2) +
    scale_color_manual(
      name = " ",
      values =  c("TRUE" = "#2E9FDF", "FALSE" = "#FC4E07"),
      labels = c(
        "TRUE" = "Werktag",
        "FALSE" = "Wochenende oder Feiertag"
      )) +
    labs(x = x_label, y = y_label) +
    theme(legend.position = "bottom",
          strip.text = element_text(size = 10)) +
    guides(color = guide_legend(override.aes = list(lwd = 3, size = 3)))
  
  ggsave(
    file_name,
    plot = p,
    width = 5.5,
    height = 3.7,
    dpi = 600
  )

}
