.PHONY: venv install fetch-repos fetch-prs analyze

venv:
	python -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

fetch-repos:
	. .venv/bin/activate && python -m code.main fetch-repos --n 200 --min-prs 100

fetch-prs:
	. .venv/bin/activate && python -m code.main fetch-prs --max-per-repo 500

analyze:
	. .venv/bin/activate && python -m code.main analyze
