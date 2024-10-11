fmt:
	black pyabtesting
	isort pyabtesting

test:
	python -m pytest . -v -s --verbose

style:
	pylint --preset SERVICE --name pyabtesting