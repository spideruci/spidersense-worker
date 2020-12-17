#!/bin/bash
# $1=spidersense-worker-path $2=spidersense-worker-branch
# $3=spiderview-path $4=spidervier-branch
echo 'FuzzyTarantula5243'|sudo service apache2 stop
sudo cp -f /var/www/spidersense-worker/config.ini /var/www
sudo cp -f /var/www/spidersense-worker/src/cfgreader.py /var/www
cd $1
git stash
git pull origin $2
sudo cp -rf $1 /var/www/
sudo cp -f /var/www/config.ini /var/www/spidersense-worker
sudo cp -f /var/www/cfgreader.py /var/www/spidersense-worker/src

cd $3
git stash
git pull origin $4
npm run-script build
sudo rm -rf /var/www/spidersense-view
sudo mkdir /var/www/spidersense-view
sudo cp -rf $3/build/* /var/www/spidersense-view

sudo service apache2 start
