set -e
flake8 . --count --exit-zero --show-source --max-complexity=10 --max-line-length=127 --statistics