import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime, timedelta

BOTH_COLOR = 'green'
FIRST_COLOR = 'goldenrod'

def unaccumulate(acc_list):
	ret = []
	prev_acc = 0
	for this_day_acc in acc_list:
		diff = this_day_acc - prev_acc
		ret.append(diff)
		prev_acc = this_day_acc
	return ret

def est_second_shots_needed(acc_both_shots, acc_first_shot_only, dates, this_day):
	all_second_shots_given = acc_both_shots[-1:][0]
	twelve_weeks_ago = this_day + timedelta(weeks = -12)
	if twelve_weeks_ago < dates[0]:
		twelve_weeks_ago = dates[0]
	index = 0
	while dates[index] < twelve_weeks_ago:
		index += 1
		if index >= len(dates):
			break
	all_second_shots_due = acc_first_shot_only[index]
	second_shots_needed = all_second_shots_due - all_second_shots_given
	if second_shots_needed < 0:
		second_shots_needed = 0
	return second_shots_needed

def get_next_day(yesterday):
	return yesterday + timedelta(days=1)

def dates_as_datetime(dates):
	dates_dt = []
	for date in dates:
		dates_dt.append(datetime.strptime(date, '%d/%m/%y'))
	return dates_dt

df = pd.read_csv('data.csv')
df.columns = [ 'Date', 'Weekly rate', 'Both doses', 'First Dose Only', 'Unvaccinated' ]
dates = df['Date']
dates_dt = dates_as_datetime(dates)
weekly_rates = df['Weekly rate'].tolist()
acc_both_doses = df['Both doses'].tolist()
acc_first_dose_only = df['First Dose Only'].tolist()
unvaccinated = df['Unvaccinated']

NUMBER_ACTUAL_ENTRIES = len(acc_first_dose_only)
UK_ADULT_POP = 52673 # in thousands
WEEKLY_SHOTS = weekly_rates[-1:][0]
DAILY_SHOTS = WEEKLY_SHOTS / 7
both_doses_daily = unaccumulate(acc_both_doses)
first_dose_only_daily = unaccumulate(acc_first_dose_only)

while acc_first_dose_only[-1:][0] < UK_ADULT_POP:
	this_day = get_next_day(dates_dt[-1:][0])
	second_shots_needed = est_second_shots_needed(acc_both_doses, acc_first_dose_only, dates_dt, this_day)
	if second_shots_needed > DAILY_SHOTS:
		second_shots_needed = DAILY_SHOTS
	
	if acc_first_dose_only[-1:][0] >= UK_ADULT_POP:
		second_shots_needed = DAILY_SHOTS

	first_doses = DAILY_SHOTS - second_shots_needed
		
	first_dose_only_daily.append(first_doses)
	both_doses_daily.append(second_shots_needed)
	prev_acc_first_dose_only = acc_first_dose_only[-1:][0]
	prev_acc_both_doses = acc_both_doses[-1:][0]
	new_acc_first_dose_only = prev_acc_first_dose_only + first_doses
	new_acc_both_doses = prev_acc_both_doses + second_shots_needed
	acc_first_dose_only.append(new_acc_first_dose_only)
	acc_both_doses.append(new_acc_both_doses)
	dates_dt.append(this_day)
	# print(this_day, first_doses, second_shots_needed, new_acc_first_dose_only, new_acc_both_doses)


# scaling
acc_both_doses = [ x/1000 for x in acc_both_doses ]
acc_first_dose_only = [ x/1000 for x in acc_first_dose_only ]

# plotting
fig = plt.figure()
ax = plt.gca()
plt.title('Estimated UK vaccine rollout - To all UK adults offered first dose')

ax.plot(dates_dt[:NUMBER_ACTUAL_ENTRIES], acc_first_dose_only[:NUMBER_ACTUAL_ENTRIES], color=FIRST_COLOR, label='First Dose Only')
ax.plot(dates_dt[:NUMBER_ACTUAL_ENTRIES], acc_both_doses[:NUMBER_ACTUAL_ENTRIES], color=BOTH_COLOR, label='Both doses')
ax.plot(dates_dt[NUMBER_ACTUAL_ENTRIES:], acc_both_doses[NUMBER_ACTUAL_ENTRIES:], color=BOTH_COLOR, linestyle='dotted')
ax.plot(dates_dt[NUMBER_ACTUAL_ENTRIES:], acc_first_dose_only[NUMBER_ACTUAL_ENTRIES:], color=FIRST_COLOR, linestyle='dotted')
ax.annotate(dates_dt[-1].strftime("%d %b %Y"), xy=(dates_dt[-1],acc_first_dose_only[-1]))

ax.set_xlabel('Month')
ax.set_yticks([0, 10, 20, 30, 40, 50, 53])
ax.set_ylabel('Individuals Vaccinated (millions)')
ax.legend()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

myFmt = mdates.DateFormatter('%b %y')
ax.xaxis.set_major_formatter(myFmt)
ax.xaxis_date()

plt.savefig('output.png')