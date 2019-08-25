REM Run Application
set APP_BASE=C:/apps/mks_apps
set APP_HOME=%APP_BASE%
set PRG=mark_get_data
REM Debug options
set LOG_LEVEL=DEBUG

REM Notification options
set MAIL_LIST=%ADMIN_MAIL%
set PAGER_LIST=%ADMIN_PGR%
set MAIL_ON_ERR=T
set PAGE_ON_ERR=T

REM For Timestamps
REM export DTM=`date '+%Y%m%d.%H.%M.%S'`
REM export DT=`date '+%Y%m%d'`

set LOG_DIR=%APP_HOME%/log
set LOG_NAME=%PRG%.log
set PYTHONINTR=C:\Python37\python.exe
set PYTHONPATH=%APP_HOME%/lib

%PYTHONINTR% %APP_HOME%/lib/app/mark_dig.py %PRG%