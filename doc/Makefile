.PHONY: html apidoc clean

html: apidoc
	make -C _build html

apidoc:
	sphinx-apidoc -F -o _build ../frfformats
	sed -i "s/_build/./g" _build/Makefile

clean:
	-rm -rf _build
