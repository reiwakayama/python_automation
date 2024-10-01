# Google flight search using url query parameters

# required parameters
where_from = 'HKG'
where_to = 'DXB' # TYO for HND/NRT
departure_date = '2024-12-01'
return_date = '2024-12-02'
nonstop = 1 # 1 for nonstop, 0 for 1+ stops
roundtrip = 1 # 1 for roundtrip, 0 for oneway
currency = 'HKD'
adult = 2
# children = 0

# optional parameters - cannot input both at the same time
airline = 'cathay' # cathay, hkexpress, emirates, etc 
seat_class = '' # economy, business, or first

import inflect
p = inflect.engine()

"""
# if children == 0:
    passengers = '%20with%20' + p.number_to_words(adult) + '%20adult'
else:
    passengers = '%20with%20' + p.number_to_words(adult) + '%20adult%20and%20' + p.number_to_words(children) + '%20children'
"""

if nonstop > 0:
    nonstop = '%20nonstop'
else: nonstop = '' 

if roundtrip == 1:
    roundtrip = ''
else: 
    roundtrip = '%20oneway'

if airline == '':
    airline = ''
    passengers = '%20with%20' + p.number_to_words(adult) + '%20adult'
else:
    airline = '%20' + str(adult) + '%20seats%20on%20' + airline
    passengers = ''

if seat_class == '':
    seat_class = ''
else: seat_class = '%20' + seat_class + '%20class'

url = 'https://www.google.com/travel/flights?q=Flights%20to%20' + where_to + '%20from%20' + where_from + '%20on%20' + departure_date + '%20through%20' + return_date + passengers + nonstop + roundtrip + seat_class + airline + '&curr=' + currency

import webbrowser
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
webbrowser.get('chrome').open_new_tab(url)
