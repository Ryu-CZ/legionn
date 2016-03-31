PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin:/usr/local/sbin
export PATH

LEGIONN_PROJ =/var/www/gitlab_projects_depl/legionn

all: install

configure:
	@mkdir -p $(LEGIONN_PROJ)
	@echo 'configuration done'

install:
	make configure
	cp ./legionn.py $(LEGIONN_PROJ)/
	cp ./config.py $(LEGIONN_PROJ)/
	cp -r ./cores/ $(LEGIONN_PROJ)/
	@echo 'installation done'