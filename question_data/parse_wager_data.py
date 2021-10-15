import pandas as pd
from string import printable


xls = pd.ExcelFile(r"UK_Questions_2018.xlsx")

sheet = xls.parse(0, header=None)

#print(sheet.columns.ravel())
questions = []
answers = []
count = 0
for row in sheet[1].tolist():
	if count >= 3:
		questions.append(row)
	count = count + 1
count = 0
for row in sheet[2].tolist():
	if count >= 3:
		answers.append(row)
	count = count + 1
file = open("UK_wager_data", "w+")
for i in range(len(questions)):
	ques_list = list(filter(lambda x: x in printable, questions[i]))
	ques_str = "".join(ques_list)
	ans_list = list(filter(lambda x: x in printable, str(answers[i])))
	ans_str = "".join(ans_list)
	file.write(str(ques_str)+"\n"+str(ans_str)+"\n")
file.close()


xls = pd.ExcelFile(r"WitsWagers_Canada.xls")

sheet = xls.parse(0, header=None)

questions = []
answers = []
count = 0
for row in sheet[1].tolist():
	if count >= 1:
		questions.append(row)
	count = count + 1
count = 0
for row in sheet[3].tolist():
	if count >= 1:
		answers.append(row)
	count = count + 1
file = open("canada_wager_data", "w+")
for i in range(len(questions)):
	if str(questions[i]) == "nan":
		continue
	ques_list = list(filter(lambda x: x in printable, questions[i]))
	ques_str = "".join(ques_list)
	ans_list = list(filter(lambda x: x in printable, str(answers[i])))
	ans_str = "".join(ans_list)
	file.write(str(ques_str)+"\n"+str(ans_str)+"\n")
file.close()