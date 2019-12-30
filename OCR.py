import http.client
import urllib.request
import urllib.parse
import urllib.error
import base64
import sys
import json
import time


def getCardName(series, idx):
    p = './{}/name_{:03d}.png'.format(series, idx)
    f = open(p, 'rb')
    data = f.read()
    f.close()

    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '36bcb76551c34ddca4405d17be54ad03',
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'language': 'unk',
        'detectOrientation ': 'true',
    })

    try:
        conn = http.client.HTTPSConnection(
            'forptcg.cognitiveservices.azure.com')
        conn.request("POST", "/vision/v1.0/ocr?%s" % params, data, headers)
        response = conn.getresponse()
        jsonData = response.read()
        conn.close()

        name = ""
        print("Get data\n=================\n{}\n".format(jsonData))

        jsonObj = json.loads(jsonData)
        if "error" in jsonObj and (jsonObj["error"]["code"] == 429 or jsonObj["error"]["code"] == "429"):
            return "retry"

        if len(jsonObj["regions"]) <= 0:
            return ""
        if len(jsonObj["regions"][0]["lines"]) <= 0:
            return ""
        for w in jsonObj["regions"][0]["lines"][0]["words"]:
            name += w["text"]
        return name
    except Exception as e:
        print(e)
        return "exception"


if len(sys.argv) != 4:
    print("Usage: {0} <series> <start> <end>")
    sys.exit(1)

series = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])

names = []
for i in range(start, end+1):
    print("Handling image {} - {}".format(series, i))

    failCount = 0
    while failCount <= 5:
        failCount += 1
        name = getCardName(series, i)
        if name == "retry":
            time.sleep(60)
        elif name == "exception":
            time.sleep(5)
        else:
            break

    names.append(name)
    print("{}\n=================".format(name))

print(json.dumps(names))
with open('series_{}_name.js'.format(series), 'w', encoding='utf8') as json_file:
    json.dump(names, json_file, ensure_ascii=False)
