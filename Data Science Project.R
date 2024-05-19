covid_dataset = read_csv("owid-covid-data.csv")
WorldBank_dataset = read_csv("worldbank_population.csv")
covid_dataset = covid_dataset %>% filter(nchar(iso_code) == 3) %>% filter(population >= 1000000)
covid_dataset_future = covid_dataset %>% mutate(new_deaths_smoothed_2wk = lead(new_deaths_smoothed, n = 14))
WorldBank_dataset = WorldBank_dataset %>% select(-`Series Name`) %>% pivot_wider(names_from = `Series Code`, values_from = `2023 [YR2023]`)
mergred_dataset = inner_join(covid_dataset_future, WorldBank_dataset, by=c('iso_code'='Country Code', 'location'='Country Name'))
#Taking out some NA's that might affect the
mergred_dataset = mergred_dataset %>% filter(is.na(new_deaths_smoothed) == FALSE) %>% 
  filter(is.na(gdp_per_capita) == FALSE) %>% filter(is.na(population) == FALSE) %>% 
  filter(is.na(life_expectancy) == FALSE) %>% filter(is.na(human_development_index) == FALSE) %>% 
  filter(is.na(population_density) == FALSE) %>% filter(is.na(total_deaths) == FALSE) %>% 
  filter(is.na(new_deaths_smoothed_2wk) == FALSE) %>% filter(is.na(median_age) == FALSE)
#2B
predict_variable = mergred_dataset %>% 
  mutate(variable3 = new_deaths_smoothed / population_density,
         variable2 = (as.numeric(SP.POP.80UP.FE) + as.numeric(SP.POP.80UP.MA)) / as.numeric(SP.POP.TOTL),
         variable1 = life_expectancy * human_development_index)

#2C
training_variable = predict_variable %>% filter(date < as.Date("2023-01-01"))
test_variable = predict_variable %>% filter(date >= as.Date("2023-01-01"))

#2d
result1 = lm(new_deaths_smoothed_2wk~new_cases_smoothed+gdp_per_capita+diabetes_prevalence+variable1+SP.POP.TOTL, data = training_variable)
result2 = lm(new_deaths_smoothed_2wk~new_deaths_smoothed+gdp_per_capita+total_deaths+life_expectancy+variable3, data = training_variable)
result3 = lm(new_deaths_smoothed_2wk~excess_mortality+median_age+ handwashing_facilities+total_vaccinations+population, data = training_variable)
result4 = lm(new_deaths_smoothed_2wk~diabetes_prevalence+cardiovasc_death_rate+male_smokers+female_smokers+extreme_poverty, data = training_variable)
result5 = lm(new_deaths_smoothed_2wk~handwashing_facilities+variable1+variable2+new_vaccinations_smoothed_per_million+population_density, data = training_variable)

#3a
Jan_Jun_data = test_variable %>% filter(date < as.Date("2023-07-01"))
root_mean_squared_result1 = rmse(result1, Jan_Jun_data)
root_mean_squared_result2 = rmse(result2, Jan_Jun_data)
root_mean_squared_result3 = rmse(result3, Jan_Jun_data)
root_mean_squared_result4 = rmse(result4, Jan_Jun_data)
root_mean_squared_result5 = rmse(result5, Jan_Jun_data)

#3b
rmse_result = Jan_Jun_data %>% group_by(location, population) %>% 
  summarise(rmse(model= result2, data=cur_data())) %>% arrange(-population)

#plots
most_recent = Jan_Jun_data %>% filter(date == "2023-06-30")
ggplot(data = Jan_Jun_data) + geom_point(mapping = aes(y=new_deaths_smoothed_2wk, x=new_cases_smoothed), na.rm = TRUE)
ggplot(data = most_recent) + geom_point(mapping = aes(y=new_deaths_smoothed, x=(as.numeric(SP.POP.80UP.FE)+as.numeric(SP.POP.80UP.MA)))) + xlab("Population over 80 years (SP.POP.80UP.FE+SP.POP.80UP.MA)")

rmse_result_top_20 = rmse_result %>% ungroup() %>% select(location, `rmse(model = result2, data = cur_data())`) %>% top_n(20)