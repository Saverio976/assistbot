PYTHON=python3
SHELL=zsh --interactive

shell:
	. ./.venv/bin/activate && echo "You are in a virtual environment" && ${SHELL}

.venv:
	${PYTHON} -m venv .venv

install:	.venv
	. ./.venv/bin/activate && pip install -r ./requirements.txt
