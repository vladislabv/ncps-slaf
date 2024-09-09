#' Will plot Raw Time Series with missing values and duplicated values.
#'
#' @param df Time Series or a DataFrame you want to Plot.
#' @param x x-Values.
#' @param y y-Values.
#' @param color Column for duplicated_values (TRUE or FALSE if duplicated)
#' @param missing_value Column where values are missing within a Time-Series (TRUE or FALSE if missing)
#' @param file_name Where the plot will be safed.
#'
plot_raw_data <- function(df, x, y, color, missing_value, file_name) {
  duplicated_data <- df |>
    filter(!!sym(color) == TRUE)
  
  missing_data <- df |>
    filter(!!sym(missing_value) == TRUE)
  
  p <- ggplot(df, aes(x = !!sym(x), y = !!sym(y))) +
    geom_line(aes(color = "Regulaere Zeitreihe"), lwd = 0.1, alpha=0.5) +
    geom_point(
      data = duplicated_data,
      aes(
        x = !!sym(x),
        y = !!sym(y),
        color = "Duplikate",
      ),
      shape=18,
      size = 1.8
    ) +
    geom_point(data = missing_data,
               aes(
                 x = !!sym(x),
                 y = !!sym(y),
                 color = "Fehlende Werte",
               ),
               shape=16,
               size = 1.8) +
    scale_color_manual(
      values = c(
        name = " ",
        "Regulaere Zeitreihe" = "black",
        "Duplikate" = "darkred",
        "Fehlende Werte" = "#FF0000"
      ),
      labels = c(
        "Regulaere Zeitreihe" = "Regulaere Zeitreihe",
        "Duplikate" = "Duplikate",
        "Fehlende Werte" = "Fehlende Werte"
      )
    ) +
    labs(x = "Zeitstempel", y = "Stromverbrauch [MW]", color = "") +
    theme(legend.position = "bottom") +
    guides(color = guide_legend(override.aes = list(lwd = 3, size = 3)))
    
  
  
  ggsave(
    file_name,
    plot = p,
    width = 5.5,
    height = 3.7,
    dpi = 600
  )
  
}