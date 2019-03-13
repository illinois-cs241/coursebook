# Scripts

* `__init__.py` Init to make a python package
* `deploy.sh` Script to run in travis deploy stage
* `script.sh` Script to run in travis script stages
* `install.sh` Script to run in travis install stage
* `gen_order.py` Generates the latex order file from the yaml file
* `gen_wiki.py` Generates a wiki given an order file and output directory
* `pandoc_header_filter.py` Outputs a yaml block to stderr given the metadata of the file
* `pandoc_wiki_filter.py` Filters a latex wiki page with additional add ons
* `push_to_wiki.sh` Script to run in the push to wiki stage
* `site_cleanup.sh` Script to clean up pushing to the site
* `site_deploy.sh` Script to deploy to the site
* `site_retry.sh` Script to retry
