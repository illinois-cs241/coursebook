#!/bin/bash

for i in `seq 0 ${NUM_RETRIES}`; 
do 
	bash site_deploy.sh && break || (bash site_cleanup.sh || sleep ${BUILD_TIME})
done
