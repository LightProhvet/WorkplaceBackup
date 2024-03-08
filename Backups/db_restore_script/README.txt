1) put the db_restore.sh file in your root direcory

2) add new alias to your root .bashrc file:
    alias dbrestore='source ~/db_restore.sh'

3) download db backup zip from server and extract it
    - the filestore directory needs to be named as 'filestore'
    - the database dump file needs to be named as 'dumb.sql' or 'dump.dmp'

4) cd to the extracted folder and run the following command:
    dbrestore -d DB_NAME -u DB_USER -p POSTGRES_CONTAINER_NAME -o ODOO_CONTAINER_NAME

Required options:
 -d DB_NAME         the name of the downloaded database
 -u DB_USER         database user defined in odoo.conf
 -p DB_CONTAINER    database docker container name
 -o ODOO_CONTAINER  odoo docker container name

Optional options:
 -f DB_FILE_TYPE    database dump file type (sql|dmp); default = sql
 -g ODOO_DATA_PATH  data directory path in odoo container; default = /var/lib/odoo
 -n 1               skip calling neutralize command (neutralize works from v16)

EXAMPLE:
dbrestore -d tarmeko_live_1 -u odoo -p postgres_12_tarmeko -o odoo_tarmeko -n


dbrestore -d warmeston_live_1 -u odoo -p postgres_14_warmeston -o odoo_warmeston