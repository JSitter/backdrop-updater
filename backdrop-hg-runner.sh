chmod 755 ./d7-updater.py
allparams=${@}
scl enable rh-python35 "./backdrop-updater.py $allparams"