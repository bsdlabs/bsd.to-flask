#

deploy:
	rsync --delete -re ssh ./bsdto niobe.bsdlabs.io:/usr/local/bsdto/
	rsync -e ssh ./setup.py niobe.bsdlabs.io:/usr/local/bsdto/
	rsync -e ssh ./requirements.txt niobe.bsdlabs.io:/usr/local/bsdto/
