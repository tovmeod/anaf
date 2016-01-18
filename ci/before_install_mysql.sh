pip install -q mysql-python
mysql -e "SHOW VARIABLES LIKE 'max_allowed_packet';"
mysql -e "SHOW VARIABLES LIKE 'wait_timeout';"
mysql -e "SET GLOBAL max_allowed_packet=134217728;"
mysql -e "SET GLOBAL wait_timeout=28800;"
mysql -e "SHOW VARIABLES LIKE 'max_allowed_packet';"
mysql -e "SHOW VARIABLES LIKE 'wait_timeout';"