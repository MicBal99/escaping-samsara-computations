.PHONY: install verify solve test

install:
	python -m pip install -r requirements.txt

verify:
	PYTHONPATH=. python scripts/run_all.py

solve:
	PYTHONPATH=. python scripts/run_all.py --solvers

test:
	PYTHONPATH=. python -m unittest discover -s tests -v
