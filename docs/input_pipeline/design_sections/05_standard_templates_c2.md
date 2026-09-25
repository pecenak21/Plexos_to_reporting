## 5. Standard templates (C2)

Blank CSVs APS copies and fills in for data not currently fed into the model at all. One per granularity × shape:

```
template_wide_annual.csv          Year, <Object 1>, <Object 2>, ...
template_wide_monthly.csv         Year, Month, <Object 1>, ...
template_wide_daily.csv           Year, Month, Day, <Object 1>, ...
template_wide_hourly.csv          Year, Month, Day, Period, <Object 1>, ...
template_single_annual.csv        Year, Value
template_single_monthly.csv       Year, Month, Value
template_single_daily.csv         Year, Month, Day, Value
template_single_hourly.csv        Year, Month, Day, Period, Value
```

Eight shapes maximum. `[ANSWERED]` — which are actually needed is not known yet, so build all eight rather than waiting for real "new data" examples. Generate them from one definition; an unused template costs nothing and a missing one costs a round trip.

A filled-in template is indistinguishable from preprocessor output downstream — same `source_path` field, same handling, no flag anywhere marking it as "new."
