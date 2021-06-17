import basic
while True:
	# interpreter prompt
	text = input('basic >> ')
	if text.strip() == "": 
		continue ##remove any wite space from either end
	result,error = basic.run('<stdin>',text)

	if(error):
		print(error.as_string())
	elif result:
		print(repr(result))