fmt:
	black -l 99 abtestools
	isort -l 99 abtestools

test:
	python -m pytest . -v -s --verbose

style:
	pylint --preset SERVICE --name abtestools