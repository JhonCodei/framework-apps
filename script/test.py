



# import datetime
#
# def float_to_full_date(ff):
# 	temp  = datetime.datetime(1900, 1, 1)
# 	delta = datetime.timedelta(days=ff)
# 	return temp + delta
#
# fec = 43678.0
#
# print(float_to_full_date(fec))

st = '2019-08-03 00:00:00'

if " " in st:
	x = st.split(" ")
	print(x)
else:
	print(":(")
