import data
import reports





lb = data.fetch_leaderboard(142, 161)
print(reports.friends(lb, "uuazed"))

exit()


lb = data.fetch_leaderboard(56, 162)
print(lb[lb.username == "uuazed2"].iloc[0])

print(reports.payments(lb, ['uuazed2']))
print(reports.payments(lb, ['uuazed', 'uuazed2', 'uuazed3']))
print(reports.payments(lb, ['anna1', 'anna2', 'anna3']))
print(reports.payments(lb, ['uuazed', 'uuazed2', 'uuazed3', 'anna1', 'anna2', 'anna3']))


print(reports.reputation_bonus(162))
