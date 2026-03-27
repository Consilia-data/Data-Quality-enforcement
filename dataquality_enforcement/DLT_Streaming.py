# Databricks notebook source
import dlt
from pyspark.sql.functions import col,when

rules={
    "valid_heartrate": "heartrate is NOT NULL",
    "valid_device_id": "device_id is NOT NULL",
    "valid_device_id_range": "device_id> 110000"
}


@dlt.table(table_properties={"quality": "silver"}
           )

@dlt.expect_all_or_drop(rules)
def bpm_silver():
    return (
        dlt.read_stream("bronze_bpm")
            .select("*", when(col("heartrate") <=0, "Negative BPM").otherwise("OK").alias("bpm_check"))
            .withWatermark("time","30 seconds")
            .dropDuplicates(["device_id", "time"])
            
            )        

# COMMAND ----------

quarantine_rules={}
quarantine_rules["invalid_record"]=f"NOT({' AND '.join(rules.values())})"


@dlt.table
@dlt.expect_all_or_drop(quarantine_rules)
def bpm_quarantine():
    return(
        dlt.read_stream("bronze_bpm")
    )

