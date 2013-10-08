MySQL Log Watcher
==========

Watches MySQL's general_log for changes and prints out nicely formatted SQL queries. Handy if you use ORM.

![Screenshot](https://raw.github.com/LukasHurych/MySQL-Log-Watcher/master/screen.png)

Requirements
----------
- [Python 2.6+](http://www.python.org/getit/releases/2.6/)
- [Pygments](http://pygments.org/)

Installation
----------
You need to enable general_log_file in your my.cnf config file.

        [mysqld]
        general_log_file        = /var/log/mysql/mysql.log
        general_log             = 1

and restart database server.

Mac OS X users: if you already don't have mysql's config file, create empty one in /etc/my.cnf

Now you can start the watcher

        python watcher.py
