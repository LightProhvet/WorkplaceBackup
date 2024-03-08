#!/bin/bash

# Assign default values to variables
DB_NAME=''
DB_USER=''
DB_CONTAINER=''
ODOO_CONTAINER=''
DB_FILE_TYPE='sql'
ODOO_DATA_PATH='/var/lib/odoo'
SKIP_NEUTRALIZE=0

# Parse command line arguments
while getopts ":d:u:p:o:f:g:n:" opt; do
  case $opt in
    d) DB_NAME="$OPTARG"
    ;;
    u) DB_USER="$OPTARG"
    ;;
    p) DB_CONTAINER="$OPTARG"
    ;;
    o) ODOO_CONTAINER="$OPTARG"
    ;;
    f) DB_FILE_TYPE="$OPTARG"
    ;;
    g) ODOO_DATA_PATH="$OPTARG"
    ;;
    n) SKIP_NEUTRALIZE=1
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done


# Check that all required arguments have been provided
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_CONTAINER" ] || [ -z "$ODOO_CONTAINER" ]; then
  echo "Error: the following arguments are required and cannot be empty." >&2
  echo "  -d  the name of the downloaded database" >&2
  echo "  -u  database user defined in odoo.conf" >&2
  echo "  -p  database docker container name" >&2
  echo "  -o  odoo docker container name" >&2
  echo "" >&2
  echo "Optional commands:" >&2
  echo "  -f  database dump file type (sql|dmp); default = sql" >&2
  echo "  -g  data directory path in odoo container; default = /var/lib/odoo" >&2
  echo "  -n  skip calling neutralize command (neutralize works from v16); default = 0" >&2
  echo "" >&2

  return 1
fi

# check if filestore directory exists in the current directory
[[ ! -d filestore ]] && { echo "ERROR: directory 'filestore' no dot exist"; return 1;}

# check if dump file exists in the current directory
if [[ $DB_FILE_TYPE == 'dmp' ]]; then
  [[ ! -f dump.dmp ]] && { echo "ERROR: dump.dmp no dot exist"; return 1;}
else
  [[ ! -f dump.sql ]] && { echo "ERROR: dump.sql no dot exist"; return 1;}
fi

# terminate existing connections to the database
docker exec -it $DB_CONTAINER psql -U $DB_USER -d postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '${DB_NAME}';"

# drop and recreate the database
docker exec -it $DB_CONTAINER psql -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS \"${DB_NAME}\";"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d postgres -c "CREATE DATABASE \"${DB_NAME}\";"

# import database
if [[ $DB_FILE_TYPE == 'dmp' ]]; then
  cat db.dmp | docker exec -i $DB_CONTAINER pg_restore -U $DB_USER --dbname "$DB_NAME" --no-owner --no-privileges
else
  cat dump.sql | docker exec -i $DB_CONTAINER psql -d $DB_NAME -U $DB_USER
fi

# neutralize
if [[ $SKIP_NEUTRALIZE == 0 ]]; then
  docker exec -it $ODOO_CONTAINER odoo neutralize -d $DB_NAME
else
  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "UPDATE ir_mail_server SET active=false, smtp_host='blablabla';"
  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "UPDATE fetchmail_server SET active=false, server='blablabla';"
  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "UPDATE ir_cron SET active=false;"
fi

## copy filestore
docker exec -it $ODOO_CONTAINER bash -c "rm -rf ${ODOO_DATA_PATH}/filestore/${DB_NAME}"
docker exec -it $ODOO_CONTAINER bash -c "mkdir -p ${ODOO_DATA_PATH}/filestore/${DB_NAME}"
docker cp filestore/. $ODOO_CONTAINER:$ODOO_DATA_PATH/filestore/$DB_NAME/.
docker exec -it --user root $ODOO_CONTAINER bash -c "chown -R odoo:odoo ${ODOO_DATA_PATH}/filestore"
docker exec -it --user root $ODOO_CONTAINER bash -c "chmod -R 777 ${ODOO_DATA_PATH}/filestore"

# fix assets
docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view';"
