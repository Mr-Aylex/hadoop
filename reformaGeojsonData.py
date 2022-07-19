import json

def reformaGeoJson(cause,year):

    # input_data = {
    #     'Afghanistan': '25616',
    #     'United Arab Emirates': '5616',
    #     'Armenia': '25616',
    # }
    # cause = 'test_death'

    input_data = filter_data(cause, year)

    with  open('./new_test.geojson', 'r') as f:
        geojson = json.load(f)

        for fea in geojson['features']:
            pay_target = fea['properties']['NAME']

            if pay_target not in input_data.keys():
                input_data[pay_target] = 0
            death = input_data[pay_target]

            fea['properties'][cause] = death

    newf = open("./testdata.geojson",'w')
    newf.write(json.dumps(geojson, indent=4))
    newf.close()


def filter_data(cause,year):
    outputData = dict()
    with  open('./annual-number-of-deaths-by-country-and-year.json','r') as f:
        data = json.load(f)
        for pay,propreties in data[year].items():
            if propreties is not None and cause in propreties.keys() and propreties[cause] is not None:
                outputData[pay] = propreties[cause]
            else :
                outputData[pay] = 0
    return outputData

