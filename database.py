from sqlalchemy import * 
from sqlalchemy.ext.declarative import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import func
from sqlalchemy.orm.exc import NoResultFound 
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import OperationalError 

import os
import models

os.remove('somefile.txt')
conn_str = 'mysql://root:testlab@172.16.19.2/haproxy'
engine = create_engine(conn_str, pool_size=50, pool_recycle=3600)
Base = declarative_base()
Base.metadata.create_all(engine) 
Session = sessionmaker(bind=engine)
session = Session()
if session:
    with open('somefile.txt', 'a') as the_file:
        the_file.write('global' + os.linesep)
        the_file.write('    log /dev/log local0' + os.linesep)
        the_file.write('    log /dev/log local1 notice' + os.linesep)
        the_file.write('    chroot /var/lib/haproxy' + os.linesep)
        the_file.write('    stats socket /run/haproxy/admin.sock mode 660 level admin' + os.linesep)
        the_file.write('    stats timeout 30s' + os.linesep)
        the_file.write('    user haproxy' + os.linesep)
        the_file.write('    group haproxy' + os.linesep)
        the_file.write('    daemon' + os.linesep)
        the_file.write('    # Default SSL material locations' + os.linesep)
        the_file.write('    ca-base /etc/ssl/certs' + os.linesep)
        the_file.write('    crt-base /etc/ssl/private' + os.linesep)
        the_file.write('    # Default ciphers to use on SSL-enabled listening sockets.' + os.linesep)
        the_file.write('    # For more information, see ciphers(1SSL).' + os.linesep)
        the_file.write('    ssl-default-bind-ciphers kEECDH+aRSA+AES:kRSA+AES:+AES256:RC4-SHA:!kEDH:!LOW:!EXP:!MD5:!aNULL:!eNULL' + os.linesep)

if session:
    with open('somefile.txt', 'a') as the_file:
        the_file.write('defaults' + os.linesep)
        d = session.query(models.Default).one()
        if d:
            print d.retries
            the_file.write('    log       global' + os.linesep)
            the_file.write('    option    httplog' + os.linesep)
            the_file.write('    option    dontlognull' + os.linesep)
            the_file.write('    maxconn ' + str(d.maxconn) + os.linesep)
            the_file.write('    retries ' + str(d.retries) + os.linesep)
            the_file.write('    timeout connect ' + d.timeout_connect + os.linesep)
            the_file.write('    timeout client ' + d.timeout_client + os.linesep)
            the_file.write('    timeout server ' + d.timeout_server + os.linesep)
            if d.option_redispatch != 0:
                the_file.write('    option redispatch' + os.linesep)       
            if d.option_httpclose != 0:
                the_file.write('    option httpclose' + os.linesep)       
            the_file.write('    errorfile 400 /etc/haproxy/errors/400.http' + os.linesep)
            the_file.write('    errorfile 403 /etc/haproxy/errors/403.http' + os.linesep)
            the_file.write('    errorfile 408 /etc/haproxy/errors/408.http' + os.linesep)
            the_file.write('    errorfile 500 /etc/haproxy/errors/500.http' + os.linesep)
            the_file.write('    errorfile 502 /etc/haproxy/errors/502.http' + os.linesep)
            the_file.write('    errorfile 503 /etc/haproxy/errors/503.http' + os.linesep)
            the_file.write('    errorfile 504 /etc/haproxy/errors/504.http' + os.linesep)


if session:
    rows = session.query(models.Frontend).all()
    for r in rows:
        print r.name,r.bind_address,r.bind_port,r.default_backend,r.mode
        with open('somefile.txt', 'a') as the_file:
            the_file.write('frontend ' + r.name + os.linesep)
            if r.mode != 'none':
                the_file.write('    mode ' + r.mode + os.linesep)
            the_file.write('    bind ' + r.bind_address + ":" + str(r.bind_port))
            if r.bind_option:
                the_file.write(' ssl crt /etc/pki/CA/' + r.bind_option.crt_name)
            the_file.write(os.linesep)
            if r.maxconn != 0:
                the_file.write('    maxconn ' + str(r.maxconn) + os.linesep)
            the_file.write('    default_backend ' + r.default_backend + os.linesep)
    session.close_all()
    
if session:
    backends = session.query(models.Backend).join(models.BackendServer)\
                                   .options(joinedload('backend_check'))\
                                   .options(joinedload('backend_server'))\
                                   .options(joinedload('backend_server.server_option'))\
                                   .all()
    for b in backends:
        with open('somefile.txt', 'a') as the_file:
            print b.name
            the_file.write('backend ' + b.name + os.linesep)
            if b.balance_method != '':
                the_file.write('    balance ' + b.balance_method + os.linesep)
            if b.mode != 'none':
                the_file.write('    mode ' + b.mode + os.linesep)
            if b.forwardfor != 0:
                the_file.write('    forwardfor')
                if b.forwardfor_expect != '':
                    the_file.write(' except ' + b.forwardfor_expect)
                if b.forwardfor_header != '':
                    the_file.write(' header ' + b.forwardfor_header)
                the_file.write(os.linesep)
            if b.cookie != 'none':
                the_file.write('    cookie ' + b.cookie_name)
                if b.cookie_option_indirect != 0:
                    the_file.write(' indirect')
                if b.cookie_option_nocache != 0:
                    the_file.write(' nocache')
                if b.cookie_option_postonly != 0:
                    the_file.write(' postonly')
                the_file.write(os.linesep)
            if b.backend_check:
                if b.backend_check.timeout_check != '':
                    the_file.write('    timeout check ' + b.backend_check.timeout_check + os.linesep) 
                if b.backend_check.ssl_hello_check != '':
                    the_file.write('    option ssl-hello-chk' + os.linesep) 
                if b.backend_check.http_check != 0:
                    the_file.write('    option httpchk') 
                    if b.backend_check.http_url != 'none': 
                        the_file.write(' ' + b.backend_check.http_method + ' ' + b.backend_check.http_url)
                    the_file.write(os.linesep) 
                if b.backend_check.http_check_expect != 'none':
                    the_file.write('    http-check expect')
                    if b.backend_check.http_check_expect_not != 0: 
                        the_file.write(' !')
                    the_file.write(' ' + b.backend_check.http_check_expect + ' ' + b.backend_check.http_check_expect_value)
                    the_file.write(os.linesep)
                if b.backend_check.disable_on_404 != 0: 
                    the_file.write('    http-check disable-on-404' + os.linesep)
            for s in b.backend_server:
                print s.name
                the_file.write('    server ' + s.name + ' ' + s.address + ':' + str(s.port))
                if s.server_option:
                    if s.server_option.check != 0:
                        the_file.write(' check ' + s.server_option.check_inter + ' fall ' + str(s.server_option.check_fall))
                    if s.server_option.cookie_value != '':
                        the_file.write(' cookie ' + s.server_option.cookie_value)
                if s.maxconn != 0:
                    the_file.write(' maxconn ' + str(s.maxconn))
                the_file.write(os.linesep)
                
if session:
    with open('somefile.txt', 'a') as the_file:
        the_file.write('listen stats :8080' + os.linesep)            
        the_file.write('    mode http' + os.linesep)
        the_file.write('    stats enable' + os.linesep)
        the_file.write('    stats hide-version' + os.linesep)
        the_file.write('    stats realm Haproxy\ Statistics' + os.linesep)
        the_file.write('    stats uri /' + os.linesep)
        the_file.write('    #stats auth your_username:your_password' + os.linesep)
        the_file.write('    stats refresh 10s' + os.linesep)
        