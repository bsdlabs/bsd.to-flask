# bsd.to
BSD.to URL shortener

## Installation and running

BSDTo is a Flask based web application, typically run via uwsgi behind nginx.
This document explains that kind of set up.

Create a dedicated user that will run the application. Clone the repository on
the server and install into a virtualenv using `setup.py`. Install as root, not
as the dedicated user that will run the application. Set up uWSGI vassal, for
example:

```ini
[uwsgi]
processes = 2
virtualenv = /path/to/your/virtualenv
module = bsdto.main:app
env = BSDTO_DBFILE=/path/to/user/owned/bsdto.db.sqlite3
```

The dedicated user should only have the read-write access to the database file.
The path to the ini file above can be given to `uwsgi_flags` rcvar in `rc.conf`
via `--ini` flag. Alternatively add these options directly to the rcvar, eg.
`--processes=2 --virtualenv=/... --module=bsdto.main:app
--env=BSDTO_DBFILE=/path/to/...`, or use uwsgi profiles. Check out
`/usr/local/etc/rc.d/uwsgi` for more info on rcvars and how to use them.

Configure nginx to run the uWSGI application, for example:

```nginx
    server {
        listen          80;
        server_name     bsd.to;
        root            /usr/local/www/nginx-dist;

        location / {
            include         uwsgi_params;
            uwsgi_pass      unix:///path/to/uwsgi.sock;
            add_header      X-Frame-Options "DENY";
        }
    }
```

The path to the uwsgi socket is defined through the `uwsgi_socket` rcvar. Start
the `uwsgi` and `nginx` services and navigate your browser to the location
you've set up in nginx config.
