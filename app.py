from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
# import requests, json
# from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as img
import base64
from io import BytesIO
from matplotlib.figure import Figure
from pyspark.sql import SparkSession
import pyspark.sql as sql
import pyspark.sql.functions as f
from pyspark.sql.functions import concat_ws, lit

appName = "Spark SQL basic example"
# Create a SparkSession
spark = SparkSession.builder.appName(appName).getOrCreate()
print("merge of datasets")
print("Spark version:", spark.version)
bd = spark.read.csv("dada/big_dataset.csv", sep=";", header=True, inferSchema=True)

# https://pymongo.readthedocs.io/en/stable/tutorial.html
# https://matplotlib.org/
app = Flask(__name__)


@app.route("/")
def main():  # put application's code here

    country = bd.select('location').distinct().rdd.flatMap(lambda x: x).collect()
    years = bd.select('Year').distinct().rdd.flatMap(lambda x: x).collect()

    return render_template('index.html', country=country, year=years)


@app.route("/plot", methods=['POST'])
def plot():
    data = []
    if request.method == 'POST':
        year = request.form['year']
        year = int(year)
        # print(year)
        lis = ["Year", "Executions", "Meningitis", "Alzheimer", "Parkinson", "Nutritional_deficiencies", "Malaria", "Drowning",
               "Interpersonal_violence", "Maternal_disorders", "HIV/AIDS", "Drug_use_disorders", "Tuberculosis",
               "Cardiovascular_diseases", "Lower_respiratory_infections", "Neonatal_disorders", "Alcohol_use_disorders",
               "Self-harm", "Exposure_to_forces_of_nature", "Diarrheal", "Environmental_heat_and_cold_exposure",
               "Neoplasms", "Conflict_and_terrorism", "Diabetes_mellitus", "Chronic_kidney", "Poisonings",
               "Protein-energy_malnutrition", "Terrorism", "Road_injuries", "Chronic_respiratory",
               "Cirrhosis_and_other_chronic liver", "Digestive", "Fire_heat_and_hot_substances", "Acute_hepatitis"]
        data = bd.select(lis).filter(f"Year = {year}").groupBy("Year").sum()
        df_pd = data.toPandas().to_dict(orient='list')
        print(df_pd)
        print(type(df_pd))
    return render_template("sum_per_year.html", data=[df_pd], headers=lis)

#plotly
@app.route('/death', methods=['POST', 'GET'])
def death():
    if request.method == 'POST':
        year = request.form['year']
        country = request.form['country']
        print(country)

        print(year, country)
        data = bd.filter(f"Year == {int(year)}").filter(f"location == '{country}'")
        data.show()
        df_pd = data.toPandas().to_dict(orient='list')
        if df_pd is None:
            return "No data for this year and country"
        print(df_pd)
        # data = df_pd[0]
        del df_pd['Year']
        del df_pd['location']
        if 'Code' in df_pd.keys():
            del df_pd['Code']
        names = df_pd.keys()
        values = df_pd.values()
        print(names)
        print(values)
        values = [0 if i[0] == None else i[0] for i in values]
        fig, ax = plt.subplots()
        ax.bar(names, values, label="death")
        ax.legend()
        for tick in ax.get_xticklabels():
            tick.set_rotation(55)
        plt.savefig("static/img/death_per_country.jpg")
        return render_template("death.html", data=df_pd)


@app.route('/death/<year>/<country>')
def death_per_url(year, country):
    client = MongoClient('mongodb://localhost:27017/')
    with open("annual-number-of-deaths-by-country-and-year.json", "r") as f:
        data = json.load(f)
        country = country.title()
        return render_template("death.html", data=data[year][country])


@app.route('/stats/', methods=['POST', 'GET'])
def stats():
    if request.method == 'POST':
        country = request.form['country']
        all_death = client['death']['death_data']
        el = all_death.find({"Entity": country})
        data = []
        for i in el:
            if '_id' in i.keys():
                del i['_id']
            if 'Entity' in i.keys():
                del i['Entity']
            if 'Code' in i.keys():
                del i['Code']
            data.append(i)

        df = pd.DataFrame(data)
        print(df)
        df.plot(x='Year', kind='line', figsize=(10, 5), legend=False)

        plt.savefig("static/img/map.jpg")
    return render_template("death_per_entity.html")


@app.route('/test')
def test():
    print("test")
    # client = MongoClient('mongodb://localhost:27017/')


@app.route('/agg', methods=['POST', 'GET'])
def agg():
    client = MongoClient('mongodb://localhost:27017/')
    all_death = client['death']['death_data']
    el = all_death.find_one({"Year": int(2007), "Entity": "France"})
    if el is None:
        return "No data for this year and country"
    data = el
    del el['_id']
    del el['Year']
    del el['Entity']
    if 'Code' in el.keys():
        del el['Code']
    names = el.keys()
    if request.method == 'POST':
        data = []
        for name in names:
            if name in list(request.form.keys()):
                data.append(name)
        data = [f"${el}" for el in data]
        all_death = client['death']['death_data']
        el = all_death.find({}, {"Entity": 1, "Year": 1, "total": {"$add": data}})
        dict_el = []
        for i in el:
            dict_el.append(i)
    return render_template("sum.html", data=dict_el)


@app.route('/ck')
def displayceckbox():
    client = MongoClient('mongodb://localhost:27017/')
    all_death = client['death']['death_data']
    el = all_death.find_one({"Year": int(2007), "Entity": "France"})
    if el is None:
        return "No data for this year and country"
    data = el
    del el['_id']
    del el['Year']
    del el['Entity']
    if 'Code' in el.keys():
        del el['Code']
    names = el.keys()
    fields = names
    return render_template('ckb.html', data={'fields': fields})


if __name__ == '__main__':
    app.run()
