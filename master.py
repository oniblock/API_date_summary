# import date and timedelta modules from 'datetime'
from datetime import date, timedelta
# import csv for writing the results into excel
import csv
# import requests from the API so that you get the status date for the CIPs
import requests

# define what the 'host' is so you can plug this into URLs
host = "http://10.0.64.71"
# define what the CIPs are so that you can label the results you get
cips = ['omicia', 'congenica', 'nextcode']
# define the API statuses - these will be the headers in the csv file for the figures
statuses = ["cip",
            "wk_start",
            "wk_end",
            "waiting_payload",
            "interpretation_generated",
            "files_copied",
            "dispatched",
            "transfer_ready",
            "genomes_transfer_ready",
            "transfer_complete",
            "genomes_transfer_complete",
            "rejected_wrong_format",
            "gel_qc_passed",
            "genomes_gel_qc_passed",
            "gel_qc_failed",
            "genomes_gel_qc_failed",
            "genomes_sent_to_gmcs",
            "sent_to_gmcs",
            "report_generated",
            "genomes_report_generated",
            "genomes_blocked",
            "blocked",
            "genomes_files_copied",
            "genomes_dispatched",
            "genomes_rejected_wrong_format"]
# so you don't show your password to the world, create a separate file, write your password in there, and then assign the file to a variable
pw_file = 'my_password.txt'
# you need to tell the console to go inside the pw_file and read (r) the password to input
with open(pw_file, 'r') as f:
    # password = the read of the pw_file
    password = f.readline()

# get your token to look at the requests. Note that the URL is plugging in 'host' from earlier.
response = requests.post('{host}/api/get-token/'.format(host=host), {'username': 'oniblock', 'password': password})
# the response from the above will be able to get you your token
token = response.json()['token']

# you need to define dates you're using for the code
wk_end_date = date.today()
# you can define one day in relation to another. Below says "the start date is 7 days before the end date"
wk_start_date = wk_end_date - timedelta(7)
# you don't want the results for all of the history of time. Define the date parameter that you want it to pick out. In this case, a year
last_year = wk_end_date - timedelta(365)

# create a dictionary called "year_results". This dictionary has 3 keys "nextcode", "congenica" and "omicia" which all have empty lists
year_results = {'nextcode': [], 'congenica': [], 'omicia': []}

# the while loop. The line below says "while the week start date is greater than last year:
while wk_start_date > last_year:
    # week end date is now equal to the week start date
    wk_end_date = wk_start_date
    # week start date is now equal to the week end date - 7 days
    wk_start_date = wk_end_date - timedelta(7)
    # the code below turns below "wk_start_date" and "wk_end_date" into strings to be plugged into the URL
    wk_start_date_str = '-'.join([str(wk_start_date.day), str(wk_start_date.month), str(wk_start_date.year)])
    wk_end_date_str = '-'.join([str(wk_end_date.day), str(wk_end_date.month), str(wk_end_date.year)])
    # this is the URL where you'll be getting your data. It plugs the value for 'host' in and you are able to set the variables start_date and end_date for their respective strings
    url_path = '{host}/api/interpretationRequests/dateSummary/{start_date}/{end_date}/'.format(host=host,
                                                                                               start_date=wk_start_date_str,
                                                                                               end_date=wk_end_date_str)
    # the code below gets the data out of the URL you have created and gives the token you obtained earlier for entry
    response2 = requests.get(url_path, headers={"Authorization": "JWT " + token})
    # you're assigning the output of response2 to 'my_data'
    my_data = response2.json()
    # for the week's results, you create an empty list
    week_results = []
    # the line below says "for each CIP (Omicia, Congenica, Nextcode) that you find in the list 'CIPs'....
    for cip in cips:
        # if the data I have obtained from the URL (i.e. "my_data") contains a key called "Omicia, Congenica or Nextcode"...
        if my_data.has_key(cip):
            # update my data with the following fieldnames
            my_data[cip].update({'cip': cip, 'wk_start': wk_start_date_str, 'wk_end': wk_end_date_str})
            # append my_data into the empty list called "week_results"
            week_results.append(my_data[cip])
        # otherwise...
        else:
            # append the cip name, the start_week date and the end_week date onto the list
            week_results.append({'cip': cip, 'wk_start': wk_start_date_str, 'wk_end': wk_end_date_str})
    # then, append all of the week's results into the particular CIPs' section in the year results dictionary
    year_results[cip].append(week_results)

# here you are assigning the "results.csv" to a variable called 'fname'
fname = 'results.csv'
# open 'fname' in writer "binary" mode as a variable called "f_handle"
with open(fname, 'wb') as f_handle:
    # write f_handle as a csv file (DictWriter as it contains a dictionary), 'restval' is the filler for where there aren't any values to plug in (e.g. CIP hasn't dispatched any cases in the week), fieldnames decides what the headings for the columns will be.
    writer = csv.DictWriter(f_handle, restval=0, fieldnames=statuses)
    writer.writeheader()
    # for each cip and it's data in the year results items...
    for cip, data in year_results.items():
        # for each row of the data...
        for row in data:
            # for each week in the row
            for wk in row:
                # write the values for the week in the row.
                writer.writerow(wk)
