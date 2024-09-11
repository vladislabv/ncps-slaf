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
plot_forecast_nn <- function(all_forecasts, metric_results, df,
                             month_to_plot, days_to_plot, raw_fc, prefix,
                             name_for_model, aep_data) {
  
  best_forecast <- metric_results |>
    filter(MAPE == min(MAPE[MAPE > 0])) |>
    slice(1) |>
    select(.model)
  
  
  name_of_best_model <- best_forecast$.model
  
  print("Best Model is:")
  print(name_of_best_model)
  
  filtered_power_consum <- df |>
    mutate(AEP_MW = AEP_MW) |>
    filter(day(Datetime) < days_to_plot) |>
    filter((year(Datetime) == 2017 & month(Datetime) <= month_to_plot)  
           | (year(Datetime) == 2016 & month(Datetime) == 12))
  
  filtered_aep_data <- aep_data |>
    mutate(AEP_MW = AEP_MW) |>
    filter(day(Datetime) < days_to_plot) |>
    filter((year(Datetime) == 2017 & month(Datetime) <= month_to_plot)  
           | (year(Datetime) == 2016 & month(Datetime) == 12 & day(Datetime) > 20))
  
  data_for_datetime <- df |>
    filter(year(Datetime) == 2017)
  data_for_datetime <- data_for_datetime[1:nrow(data_for_datetime),]
  
  dobuled_data <- bind_rows(as.data.frame(data_for_datetime), as.data.frame(data_for_datetime))
  all_fc <- raw_fc |> 
    mutate(Datetime = dobuled_data$Datetime,
           AEP_MW = dobuled_data$AEP_MW,
           WorkDay = dobuled_data$WorkDay) 

  single_best_forecast <- raw_fc |>
    filter(.model == name_of_best_model) |>
    mutate(Datetime = data_for_datetime$Datetime,
           AEP_MW = data_for_datetime$AEP_MW,
           WorkDay = data_for_datetime$WorkDay) 

  print("Validating right positions, should be close to 0: ")
  print(sum(data_for_datetime$AEP_MW - data_for_datetime$y_true))
  print(sum(single_best_forecast$AEP_MW - single_best_forecast$y_true))
  print(sum(all_fc$AEP_MW - all_fc$y_true))
  
  p <- ggplot() +
    geom_line(data = filtered_aep_data,
              lwd = 0.3, alpha=0.3,
              aes(x = Datetime, y = AEP_MW, color = "Tatsaechliche\nStromerzeugung [MW]")) +
    geom_line(data = all_fc |> filter(month(Datetime) == 1),
              lwd = 0.2 ,
              aes(x = Datetime, y = .mean, color =.model)) +
    theme(legend.position = "bottom", strip.text = element_text(size = 12)) +
    guides(color = guide_legend(override.aes = list(lwd = 3, size = 2), title = " "),
           fill = guide_legend(title = " "))+
    labs(level = "Level")+ 
    labs(
      x = "Zeitstempel",
      y = "Stromerzeugung [MW]"
    ) +
    scale_color_manual(
      values = c(
        name = " ",
        "LNN" = "#FF9100",
        "LNN mit SLAF" = "#2E9FDF",
        "Tatsaechliche\nStromerzeugung [MW]" = "black"
      ))
  
  
  
  ggsave(
    paste0("plots/",prefix, name_of_best_model, ".png"),
    plot = p,
    width = 6.5,
    height = 3.7,
    dpi = 600
  )
  
  p <- ggplot()+
    geom_point(data = single_best_forecast, aes(x=AEP_MW, y=.mean, color=WorkDay), alpha=0.5, size=0.5) +
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


