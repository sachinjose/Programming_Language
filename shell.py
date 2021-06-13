import basic
while True:
	# interpreter prompt
	text = input('basic >> ')
	result,error = basic.run('<stdin>',text)

	if(error):
		print(error.as_string())
	elif result:
		print(repr(result))