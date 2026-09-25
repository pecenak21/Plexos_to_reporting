# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 17:40:28 2026

@author: Z20045
"""

import pandas as pd

file_path ="Load_PLEXOS.xlsx"

value_names = ["DSM_1","Embedded_DG","Incremental_DG","DistBATT"]

xls= pd.ExcelFile(file_path)

for i, sheet_name in enumerate (xls.sheet_names):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    
    value_name = value_names[i] if i< len (value_names) else "Value"
    
    year_cols =[col for col in df.columns if str(col).isdigit()]
    if "Hour" not in df.columns or not year_cols:
        print(f"Skipping sheet :{sheet_name}")
        continue
    
    df=df[["Hour"]+ year_cols].copy()
    
    out =df.melt(
        id_vars ="Hour",
        value_vars = year_cols,
        var_name="Year",
        value_name=value_name
        )
    out = out.rename(columns ={"Hour":"Period"})
    
    dt = pd.to_datetime(out["Year"].astype(str)+"-01-01") +pd.to_timedelta(out["Period"]-1,unit="h")
    
    out["Month"]=dt.dt.month
    out["Day"]=dt.dt.day
    out=out[["Year", "Month", "Day","Period", value_name]]
    out = out.sort_values(["Year",  "Period"]).reset_index(drop=True)
    safe_name="".join(c if c.isalnum() or c in " _-" else "_" for c in sheet_name)
    
    out.to_csv(f"{safe_name}.csv", index=False)
    print (f"Saved:{safe_name}.csv")
    
        
    
    