pip install -q mysql-python
echo -e "[server]\nmax_allowed_packet=64M" | tee -a /etc/mysql/conf.d/fix.cnf
service mysql restart
mysql -e "SHOW VARIABLES LIKE 'max_allowed_packet';"