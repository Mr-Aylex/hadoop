import json
import numpy as np


def reformaGeoJson(input_data ,cause, year):
    with  open('./new_test.geojson', 'r') as f:
        geojson = json.load(f)

        for fea in geojson['features']:
            pay_target = fea['properties']['NAME']

            if pay_target not in input_data.keys():
                input_data[pay_target] = 0
                # print(f"{pay_target=} no find , add 0 inside")
            # else:
                # print(f"{pay_target=} find val : {input_data[pay_target]}")
            death = input_data[pay_target]

            fea['properties'][cause] = death

    #     print(json.dumps(geojson, indent=4))
    newf = open("./templates/testdata.geojson", 'w')
    newf.write(json.dumps(geojson, indent=4))
    newf.close()


def filter_data(cause, year):
    outputData = dict()

    ignore_list = ['World','G20','Western Europe','Central Europe']

    with  open('./annual-number-of-deaths-by-country-and-year.json', 'r') as f:
        data = json.load(f)
        for pay, propreties in data[year].items():
            if propreties is not None and propreties["Code"] is None:
                print(f"{pay=} have not code")
                ignore_list.append(pay)

        for pay, propreties in data[year].items():

            if pay in ignore_list :
                continue
            if propreties is not None and cause in propreties.keys() and propreties[cause] is not None:
                outputData[pay] = propreties[cause]
            else:
                outputData[pay] = 0
    return outputData

