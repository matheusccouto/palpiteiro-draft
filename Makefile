codespaces: pip serverless
	pip install -r requirements-bigquery.txt
pip:
	pip install --upgrade pip wheel
serverless:
	npm install -g serverless@3
	npm install --save-dev serverless-step-functions
layer_bigquery.zip: pip
	mkdir python
	pip install \
		--platform manylinux2014_x86_64 \
		--implementation cp \
		--python 3.9 \
		--only-binary=:all: \
		--target python \
		-r requirements-bigquery.txt
	zip -r layer_bigquery.zip python/
	rm -r python
layers: layer_bigquery.zip