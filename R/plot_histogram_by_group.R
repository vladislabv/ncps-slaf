

plot_histogram_by_group <- function(filtered_power_consum,
                                    group_name,
                                    file_name,
                                    colors,
                                    x,
                                    x_label,
                                    y_label) {
  
  p <-
    ggplot(filtered_power_consum, aes(x = !!sym(x), fill = !!sym(group_name) )) +
    geom_histogram(alpha = 0.5, binwidth = 200, position = "dodge") +
    geom_density(fill=NA, aes(color = !!sym(group_name), y=200 * ..count..)) + 
    theme(legend.position = "bottom",
          strip.text = element_text(size = 12)) +
    labs(x = x_label, y = y_label) +
    scale_fill_manual(
      name = " ",
      values = colors,
      labels = c(
        "TRUE" = "Werktag",
        "FALSE" = "Feiertag"
      )
    ) +
    scale_color_manual(
      values = colors
    ) + 
  guides(color = "none") +
  scale_y_continuous(labels = label_comma())
  
  ggsave(
    file_name,
    plot = p,
    width = 5.5,
    height = 3.7,
    dpi = 600
  )
}