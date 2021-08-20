import requests
import json
import pprint
import datetime

urls = [
'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=414001&date=20-08-2021',
'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=414203&date=20-08-2021'
        ]




while True:
    sent = False
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            k = json.loads(response.text)
            if k['centers'] != []:
                for key, items in k.items():
                    for item in items:
                        if item['fee_type'] == 'Free':
                            final_dict = item['sessions']
                            for elements in final_dict:
                                if elements['available_capacity'] != 0 and elements['vaccine'] == 'COVISHIELD':
                                    now = datetime.datetime.now
                                    url_u = 'https://wirepusher.com/send?id=SqmpmpXTR&title={}& message={}&type=Urgent'
                                    final_url = url_u.format('Slot Available', item['name'])
                                    requests.get(final_url)
                                    sent = True
            if sent:
                exit()
