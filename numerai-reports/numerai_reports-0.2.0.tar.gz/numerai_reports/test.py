import data
import reports


lb = data.fetch_leaderboard(56, 100)
print(lb[lb.username == "uuazed2"].iloc[0])

print(reports.payments(lb, ['uuazed2']))
print(reports.payments(lb, ['uuazed', 'uuazed2', 'uuazed3']))
print(reports.payments(lb, ['anna1', 'anna2', 'anna3']))
print(reports.payments(lb, ['uuazed', 'uuazed2', 'uuazed3', 'anna1', 'anna2', 'anna3']))


df_rep = reports._reputation_bonus(162)
