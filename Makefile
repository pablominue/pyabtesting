fmt:
	black pyabtesting
	isort pyabtesting

test:
	python -m pytest . -v -s

style:
	pylint --preset SERVICE --name pyabtesting