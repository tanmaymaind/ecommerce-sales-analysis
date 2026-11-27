# DAX measures for the Power BI dashboard

Load `powerbi/cleaned_sales.csv` into Power BI Desktop and rename the table
to **Sales** — every measure below assumes that name. Create each measure
(Home → New measure) and paste the DAX exactly as written.

Revenue rule (same as the SQL/Python analysis): only `Delivered` orders
count as revenue. Cancelled/Returned value is tracked separately as lost
order value.

```dax
Total Revenue =
CALCULATE ( SUM ( Sales[revenue] ), Sales[status] = "Delivered" )
```

```dax
Total Orders =
CALCULATE ( COUNTROWS ( Sales ), Sales[status] = "Delivered" )
```

```dax
Units Sold =
CALCULATE ( SUM ( Sales[quantity] ), Sales[status] = "Delivered" )
```

```dax
Average Order Value =
DIVIDE ( [Total Revenue], [Total Orders] )
```

```dax
All Orders =
COUNTROWS ( Sales )
```

```dax
Cancelled Orders =
CALCULATE ( COUNTROWS ( Sales ), Sales[status] = "Cancelled" )
```

```dax
Returned Orders =
CALCULATE ( COUNTROWS ( Sales ), Sales[status] = "Returned" )
```

```dax
Cancellation Rate =
DIVIDE ( [Cancelled Orders], [All Orders] )
-- format this measure as a percentage in the model view
```

```dax
Lost Order Value =
CALCULATE ( SUM ( Sales[revenue] ), Sales[status] IN { "Cancelled", "Returned" } )
```

```dax
Buying Customers =
CALCULATE ( DISTINCTCOUNT ( Sales[customer_id] ), Sales[status] = "Delivered" )
```

```dax
Repeat Customers =
VAR CustOrders =
    ADDCOLUMNS (
        VALUES ( Sales[customer_id] ),
        "DeliveredOrders",
            CALCULATE ( COUNTROWS ( Sales ), Sales[status] = "Delivered" )
    )
RETURN
    COUNTROWS ( FILTER ( CustOrders, [DeliveredOrders] >= 2 ) )
```

```dax
Repeat Customer Rate =
DIVIDE ( [Repeat Customers], [Buying Customers] )
-- format this measure as a percentage in the model view
```

```dax
Category Revenue Share =
DIVIDE (
    [Total Revenue],
    CALCULATE ( [Total Revenue], ALL ( Sales[category] ) )
)
-- format as a percentage; use on the category visual
```

```dax
Region Revenue Share =
DIVIDE (
    [Total Revenue],
    CALCULATE ( [Total Revenue], ALL ( Sales[region] ) )
)
-- format as a percentage; use on the region visual
```

Notes:
- No separate "monthly revenue" measure is needed — put `Sales[month]` on
  the axis of a line/bar visual and `[Total Revenue]` as the value.
- Expected values with no filters applied (use them to check the model):
  Total Revenue ₹4,70,89,730 · Total Orders 10,133 · Average Order Value
  ₹4,647.17 · Buying Customers 2,221 · Repeat Customer Rate 79.78% ·
  Cancelled Orders 1,064 · Lost Order Value ₹69,49,561.
