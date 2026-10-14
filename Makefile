.PHONY: install test run run-live demo clean

install:
	pip install -r requirements.txt

test:
	pytest -q

# Offline demo on the bundled mock target (no ollama / no network needed).
run: demo
demo:
	python main.py --mock

# Live run against the target configured in llm.py / .env (ollama by default).
run-live:
	python main.py

clean:
	rm -rf out .pytest_cache **/__pycache__
