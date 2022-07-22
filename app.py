import json
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request
from pyspark.sql import SparkSession

appName = "Flask app"
# Create a SparkSession
spark = SparkSession.builder.appName(appName).getOrCreate()
print("Spark version:", spark.version)
bd = spark.read.csv("dada/big_dataset.csv", sep=";", header=True, inferSchema=True)

# https://pymongo.readthedocs.io/en/stable/tutorial.html
# https://matplotlib.org/
app = Flask(__name__)


@app.route("/")
def main():  # put application's code here

    country = bd.select('location').distinct().rdd.flatMap(lambda x: x).collect()
    years = bd.select('Year').distinct().sort('Year').rdd.flatMap(lambda x: x).collect()

    return render_template('index.html', country=country, year=years)


@app.route("/plot", methods=['POST'])
def plot():
    data = []
    if request.method == 'POST':
        year = request.form['year']
        try:
            year = int(year)
        except ValueError:
            return "Year must be an integer"
        # print(year)
        lis = ["Year", "Executions", "Meningitis", "Alzheimer", "Parkinson", "Nutritional_deficiencies", "Malaria", "Drowning",
               "Interpersonal_violence", "Maternal_disorders", "HIV/AIDS", "Drug_use_disorders", "Tuberculosis",
               "Cardiovascular_diseases", "Lower_respiratory_infections", "Neonatal_disorders", "Alcohol_use_disorders",
               "Self-harm", "Exposure_to_forces_of_nature", "Diarrheal", "Environmental_heat_and_cold_exposure",
               "Neoplasms", "Conflict_and_terrorism", "Diabetes_mellitus", "Chronic_kidney", "Poisonings",
               "Protein-energy_malnutrition", "Terrorism", "Road_injuries", "Chronic_respiratory",
               "Cirrhosis_and_other_chronic liver", "Digestive", "Fire_heat_and_hot_substances", "Acute_hepatitis"]
        data = bd.select(lis).filter(f"Year = {year}").groupBy("Year").sum()
        if data.isEmpty():
            return "No data"
        df_pd = data.toPandas().to_dict(orient='list')
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
        if data.isEmpty():
            return "No data for this year and country"
        df_pd = data.toPandas().to_dict(orient='list')
        # print(df_pd)
        # data = df_pd[0]
        del df_pd['Year']
        del df_pd['location']
        if 'Code' in df_pd.keys():
            del df_pd['Code']
        names = df_pd.keys()
        values = df_pd.values()
        values = [0 if i[0] == None else i[0] for i in values]
        pd.DataFrame({'maladie':names, 'nb': values}).plot.barh(x='maladie', y='nb', figsize=(15, 7))
        plt.visible = True
        plt.savefig("static/img/death_per_country.jpg")
        return render_template("death.html", data=df_pd)

@app.route('/stats/', methods=['POST', 'GET'])
def stats():
    if request.method == 'POST':
        country = request.form['country']
        if isinstance(country, str):
            data = bd.filter(f"location == '{country}'")
            df_pd = data.toPandas().to_dict(orient='records')
            data = []
            for i in df_pd:
                if '_id' in i.keys():
                    del i['_id']
                if 'Entity' in i.keys():
                    del i['Entity']
                if 'Code' in i.keys():
                    del i['Code']
                data.append(i)

            df = pd.DataFrame(data)
            df.plot(x='Year', kind='line', figsize=(10, 5), legend=False)

            plt.savefig("static/img/map.jpg")
            return render_template("death_per_entity.html")
        else:
            return "No data for this country"
    return "Invalid request"


@app.route('/test')
def test():
    print("test")
    # client = MongoClient('mongodb://localhost:27017/')


# @app.route('/agg', methods=['POST', 'GET'])
# def agg():
#
#
#     if request.method == 'POST':
#         data = []
#         key_list = list(request.form.keys())
#         # data = [f"${el}" for el in data]
#         # all_death = client['death']['death_data']
#         # el = all_death.find({}, {"Entity": 1, "Year": 1, "total": {"$add": data}})
#         req = bd.groupBy(['location', 'Year']).sum().show()
#         print(data)
#         dict_el = []
#         for i in key_list:
#             dict_el.append(i)
#     return render_template("sum.html", data=dict_el)
@app.route('/map', methods=['POST', 'GET'])
def map():
    with open("annual-number-of-deaths-by-country-and-year.json") as f:
        data = json.load(f)

    return render_template("map.html", data=dict(data))

@app.route('/ck')
def displayceckbox():
    fields = bd.columns[3:]
    return render_template('ckb.html', data={'fields': fields})


if __name__ == '__main__':
    app.run()
