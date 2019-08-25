REM Run Application

set APP_BASE=C:/apps/mks_apps
set APP_HOME=%APP_BASE%

REM Debug options
set LOG_LEVEL=DEBUG

REM Notification options
set MAIL_LIST=%ADMIN_MAIL%
set PAGER_LIST=%ADMIN_PGR%
#export MAIL_ON_ERR=T
#export PAGE_ON_ERR=T

#For Timestamps
REM export DTM=`date '+%Y%m%d.%H.%M.%S'`
REM export DT=`date '+%Y%m%d'`

set LOG_DIR=%APP_HOME%/log
REM export LOG_NAME=`basename $0`.${DTM}
set PYTHONINTR=C:\Python37\python.exe
set PYTHONPATH=%APP_HOME%/lib

%PYTHONINTR% %APP_HOME%/lib/apps/mark_dig.py AFE
