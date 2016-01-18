pip install -q mysql-python
echo -e "[server]\nmax_allowed_packet=64M" | sudo tee -a /etc/mysql/conf.d/fix.cnf
sudo service mysql reload
mysql -e "SHOW VARIABLES LIKE 'max_allowed_packet';"