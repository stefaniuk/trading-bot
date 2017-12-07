oldversion = 'v0.1a1'
version = 'v0.1a2'

clean:
	@find . -name "*.pyc" -delete

dependencies:
	@pip install .

dev-dependencies:
	@pip install -e .

release:
	@sed -ic -e s/$(oldversion)/$(version)/ setup.py tradingbot/__init__.py
	@make clean
	@git add setup.py tradingAPI/__init__.py
	@git commit -m "setup: bump to $(version)"
	@git tag $(version)
	@git push --tags
	@git push
	@python setup.py sdist bdist_wheel upload
