chmod 755 ./backdrop-updater.py
allparams=${@}
scl enable rh-python35 "./backdrop-updater.py $allparams"