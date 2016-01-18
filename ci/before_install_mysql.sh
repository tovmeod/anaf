pip install -q mysql-python
mysql -e "SHOW VARIABLES LIKE 'max_allowed_packet';"
mysql -e "SHOW VARIABLES LIKE 'wait_timeout';"
echo -e "[server]\nmax_allowed_packet=128M" | sudo tee -a /etc/mysql/conf.d/fix.cnf
echo -e "wait_timeout = 600" | sudo tee -a /etc/mysql/conf.d/fix.cnf
sudo service mysql restart
mysql -e "SHOW VARIABLES LIKE 'max_allowed_packet';"
mysql -e "SHOW VARIABLES LIKE 'wait_timeout';"