CREATE OR REPLACE PROCEDURE `retail_dataset.sp_clean_orders`()
BEGIN

  INSERT INTO `retail_dataset.final_orders`
  SELECT
    Order_ID,
    SAFE_CAST(Order_Date AS DATE),
    SAFE_CAST(Ship_Date AS DATE),
    Ship_Mode,
    Customer_Name,
    Segment,
    Country,
    City,
    State,
    Region,
    Product_ID,
    Category,
    Sub_Category,
    Product_Name,
    SAFE_CAST(Sales AS FLOAT64),
    SAFE_CAST(Quantity AS INT64),
    SAFE_CAST(Discount AS FLOAT64),
    SAFE_CAST(Profit AS FLOAT64),
    CURRENT_TIMESTAMP() AS processed_timestamp
  FROM `retail_dataset.raw_orders`
  WHERE Sales IS NOT NULL;

END;