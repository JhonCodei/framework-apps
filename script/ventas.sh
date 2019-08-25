# Run Application
export APP_BASE=/Users/owkr/Desktop/Python/framework
export APP_HOME=$APP_BASE

#/Users/owkr/Desktop/Python/framework
# Debug options
export LOG_LEVEL=DEBUG

# Notification options
export MAIL_LIST=$ADMIN_MAIL
export PAGER_LIST=$ADMIN_PGR
#export MAIL_ON_ERR=T
#export PAGE_ON_ERR=T

#For Timestamps
export DTM=`date '+%Y%m%d_owker.log'`
export DT=`date '+%Y%m%d'`

export LOG_DIR=$APP_HOME/log
export LOG_NAME=`$0`.${DTM}
export PYTHONINTR=python3
#$APP_BASE/PycharmProjects/venv/sms/bin/python3.6
export PYTHONPATH=$APP_HOME/lib

$PYTHONINTR $APP_HOME/lib/apps/ventas.py X
