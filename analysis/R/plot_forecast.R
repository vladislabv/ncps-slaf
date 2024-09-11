#' Plot best Model for single Models
#'
#' @param all_forecasts Should be all Forecasted values for all Models.
#' @param metric_results Alle the metrics for all Models (Best Model will be extracted here)
#' @param cleaned_power_consum Cleaned Power Consum Data
#' @param raw_fc Raw Forecast Data
#' @param month_to_plot Until which month the best Forecast should be plotted?
#' @param days_to_plot How many days you want to plot? 
#' 
#' @return name_of_best_model Could be for example "version_0"
#' 
#' 
plot_forecast <- function(all_forecasts, metric_results, df,
                          month_to_plot, days_to_plot, raw_fc, prefix) {
  
  best_forecast <- metric_results |>
    filter(MAPE == min(MAPE[MAPE > 0])) |>
    slice(1) |>
    select(.model)
  
  
  name_of_best_model <- best_forecast$.model
  
  print("Best Model is:")
  print(name_of_best_model)
  
  filtered_best_forecast <- all_forecasts |>
    filter(.model == name_of_best_model) |>
    left_join(df |> rename(RealPowerConsum = AEP_MW,
                                             WorkingDay = WorkDay), by = "Datetime") |>
    mutate(WorkDay = as.factor(WorkDay))
  
  single_best_forecast <- raw_fc |>
    filter(.model == name_of_best_model) |>
    filter(month(Datetime) <= month_to_plot) |>
    filter(day(Datetime) < days_to_plot) |>
    filter(year(Datetime) == 2017)
  
  filtered_power_consum <- df |>
    mutate(AEP_MW = AEP_MW) |>
    filter(day(Datetime) < days_to_plot) |>
    filter((year(Datetime) == 2017 & month(Datetime) <= month_to_plot)  
           | (year(Datetime) == 2016 & month(Datetime) == 12 & day(Datetime) > 20))
  
  
  p <- autoplot(single_best_forecast, color = "#FC4E07", alpha=0.5) +
    geom_line(data = filtered_power_consum,
              lwd = 0.4, alpha=0.2,
              aes(x = Datetime, y = AEP_MW, color = "Tatsaechliche\nStromerzeugung [MW]")) +
    geom_line(data = single_best_forecast,
              lwd = 0.2 ,
              aes(x = Datetime, y = .mean, color =
                    "Forecast")) +
    theme(legend.position = "bottom", strip.text = element_text(size = 12)) +
    guides(color = guide_legend(override.aes = list(lwd = 3, size = 2), title = " "),
           fill = guide_legend(title = " "))+
    scale_color_manual(
      values = c(
        name = " ",
        "Tatsaechliche\nStromerzeugung [MW]" = "black",
        "Forecast" = "#FC4E07"
      ),
      labels = c(
        "Tatsaechliche\nStromerzeugung [MW]" = "Tatsaechliche\nStromerzeugung [MW]",
        "Forecast" = "PROPHET"
      )
    ) +
    labs(level = "Level")+ 
    labs(
      x = "Zeitstempel",
      y = "Stromerzeugung [MW]"
    )
  
  
  
  ggsave(
    paste0("plots/",prefix, name_of_best_model, ".png"),
    plot = p,
    width = 5.5,
    height = 3.7,
    dpi = 600
  )
  
  print(names(filtered_best_forecast))
  p <- ggplot()+
    geom_point(data = filtered_best_forecast, aes(x=RealPowerConsum, y=.mean, color=WorkingDay), alpha=0.5, size=0.5) +
    geom_abline(slope = 1, intercept = 0, color = "black", lwd=0.5, alpha=0.5) +
    xlim(8000, 22000) +
    ylim(8000, 22000) +
    scale_color_manual(
      values = c(
        name = " ",
        "TRUE" = "#FF9100",
        "FALSE" = "#2E9FDF"
      ),
      labels = c(
        "TRUE" = "Werktage",
        "FALSE" = "Feiertage udn Wochenenden"
      )) +
    theme(legend.position = "bottom", strip.text = element_text(size = 12)) +
    guides(color = guide_legend(override.aes = list(lwd = 3, size = 2), title = " "),
           fill = guide_legend(title = " ")) +
    labs(
      x = "Stromerzeugung [MW]",
      y = "Vorhersage [MW]"
    )
  
  ggsave(
    paste0("plots/real_to_fc_", prefix, name_of_best_model, ".png"),
    plot = p,
    width = 5.5,
    height = 3.7,
    dpi = 600
  )
  
  return(name_of_best_model)
  
}
  
  
  