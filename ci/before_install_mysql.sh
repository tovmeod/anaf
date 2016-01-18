pip install -q mysql-python
echo -e "[server]\nmax_allowed_packet=128M" | sudo tee -a /etc/mysql/conf.d/fix.cnf
sudo service mysql restart
mysql -e "SHOW VARIABLES LIKE 'max_allowed_packet';"