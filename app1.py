from pyspark.sql import SparkSession
import pyspark.sql as sql
import pyspark.sql.functions as f
from pyspark.sql.functions import concat_ws, lit
appName = "Spark SQL basic example"
# Create a SparkSession
spark = SparkSession.builder.appName(appName).getOrCreate()
print("merge of datasets")
print("Spark version:", spark.version)
covid = spark.read.csv("dada/owid-covid-data.csv", sep=",", header=True, inferSchema=True)
df2: sql.DataFrame
df2 = covid[["date_", "location", "new_deaths"]].withColumn('Year', f.year("date_")).groupby(["Year", "location"]).sum("new_deaths")
df2 = df2.withColumnRenamed("sum(new_deaths)", "covid_death")
death = spark.read.csv("dada/annual-number-of-deaths-by-cause.csv", sep=";", header=True)
tab = "location|Code|Year|Executions|Meningitis|Alzheimer|Parkinson|Nutritional_deficiencies|Malaria|Drowning|Interpersonal_violence|Maternal_disorders|HIV/AIDS|Drug_use_disorders|Tuberculosis|Cardiovascular_diseases|Lower_respiratory_infections|Neonatal_disorders|Alcohol_use_disorders|Self-harm|Exposure_to_forces_of_nature|Diarrheal|Environmental_heat_and_cold_exposure|Neoplasms|Conflict_and_terrorism|Diabetes_mellitus|Chronic_kidney|Poisonings|Protein-energy_malnutrition|Terrorism|Road_injuries|Chronic_respiratory|Cirrhosis_and_other_chronic liver|Digestive|Fire_heat_and_hot_substances|Acute_hepatitis".split("|")

tab = "Code|Executions|Meningitis|Alzheimer|Parkinson|Nutritional_deficiencies|Malaria|Drowning|Interpersonal_violence|Maternal_disorders|HIV/AIDS|Drug_use_disorders|Tuberculosis|Cardiovascular_diseases|Lower_respiratory_infections|Neonatal_disorders|Alcohol_use_disorders|Self-harm|Exposure_to_forces_of_nature|Diarrheal|Environmental_heat_and_cold_exposure|Neoplasms|Conflict_and_terrorism|Diabetes_mellitus|Chronic_kidney|Poisonings|Protein-energy_malnutrition|Terrorism|Road_injuries|Chronic_respiratory|Cirrhosis_and_other_chronic liver|Digestive|Fire_heat_and_hot_substances|Acute_hepatitis".split("|")
death = death.withColumn("covid_death", lit(None)) #join(df2, on=['Year'])
for col in tab:
    print(col)
    df2 = df2.withColumn(col, lit(None))


big_dataset = death.unionByName(df2)
big_dataset.write.csv("dada/big_dataset.csv", sep=";", header=True, mode="overwrite")

spark.stop()
