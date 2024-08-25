

plot_raw_data <- function(df, x, y, color, missing_value, file_name) {
  duplicated_data <- df |>
    filter(!!sym(color) == TRUE)
  
  missing_data <- df |>
    filter(!!sym(missing_value) == TRUE)
  
  p <- ggplot(df, aes(x = !!sym(x), y = !!sym(y))) +
    geom_line(aes(color = "Regulaere Zeitreihe"), lwd = 0.1) +
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
        "Regulaere Zeitreihe" = "#000000",
        "Duplikate" = "orange",
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
  
  p
  
  ggsave(
    file_name,
    plot = p,
    width = 5.5,
    height = 3.7,
    dpi = 600
  )
  
}