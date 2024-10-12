fmt:
	black abtestools
	isort abtestools

test:
	python -m pytest . -v -s --verbose

style:
	pylint --preset SERVICE --name abtestools