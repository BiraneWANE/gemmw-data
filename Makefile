.PHONY: install lint test collecte dashboard

install:
	uv sync --all-extras
	uv run pre-commit install

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest --cov

collecte:
	uv run python -m gemmw.cli collecte

dashboard:
	uv run streamlit run src/gemmw/tableau_de_bord/app.py
