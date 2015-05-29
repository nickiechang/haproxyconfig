from sqlalchemy import * 
from sqlalchemy.ext.declarative import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref


from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR
        
Base = declarative_base()

class Default(Base):
    __tablename__ = 'default'
    id = Column(INT, primary_key=True)
    maxconn = Column(INT)
    timeout_connect = Column(VARCHAR)
    timeout_client = Column(VARCHAR)
    timeout_server = Column(VARCHAR)
    retries = Column(INT)
    option_redispatch = Column(TINYINT)
    option_httpclose = Column(TINYINT)

class Frontend(Base):
    __tablename__ = 'frontend'
    name = Column(VARCHAR, primary_key=True)
    bind_address = Column(VARCHAR)
    bind_port = Column(INT)
    default_backend = Column(VARCHAR)
    mode = Column(ENUM('none','tcp','http'))
    maxconn = Column(INT)
    
class BindOption(Base):
    __tablename__ = 'bind_option'
    frontend_name = Column(VARCHAR, ForeignKey('frontend.name'),primary_key=True)
    frontend = relationship('Frontend', backref=backref('bind_option', uselist=False))
    crt_name = Column(VARCHAR)

class Backend(Base):
    __tablename__ = 'backend'
    name = Column(VARCHAR, primary_key=True)
    balance_method = Column(ENUM('','source','first','static-rr','leastconn','roundrobin'))
    mode = Column(ENUM('none','tcp','http'))
    forwardfor = Column(TINYINT)
    forwardfor_expect = Column(VARCHAR)
    forwardfor_header = Column(VARCHAR)
    cookie = Column(ENUM('none','prefix','rewrite','insert'))
    cookie_name = Column(VARCHAR)
    cookie_option_indirect = Column(TINYINT)
    cookie_option_nocache = Column(TINYINT)
    cookie_option_postonly = Column(TINYINT)
    cookie_domain = Column(VARCHAR)
#    timeout_check = Column(VARCHAR)

class BackendCheck(Base):
    __tablename__ = 'backend_check'
    backend_name = Column(VARCHAR, ForeignKey('backend.name'), primary_key=True)
    backend = relationship('Backend', backref=backref('backend_check', uselist=False))
    ssl_hello_check = Column(TINYINT)
    http_check = Column(TINYINT)
    http_method = Column(ENUM('none','OPTIONS','HEAD','POST','GET'))
    http_url = Column(VARCHAR)
    http_check_expect = Column(ENUM('none','rstring','string','rstatus','status'))
    http_check_expect_not = Column(TINYINT)
    http_check_expect_value = Column(VARCHAR)
    disable_on_404 = Column(TINYINT)
    timeout_check = Column(VARCHAR)
   
class BackendServer(Base):
    __tablename__ = 'backend_server'
    name = Column(VARCHAR, primary_key=True)
    address = Column(VARCHAR)
    port = Column(INT)
    maxconn = Column(INT)
    backend_name = Column(VARCHAR, ForeignKey('backend.name'))
    backend = relationship('Backend', backref=backref('backend_server'))

class ServerOption(Base):
    __tablename__ = 'server_option'
    backend_server_name = Column(VARCHAR, ForeignKey('backend_server.name'), primary_key=True)
    backendserver = relationship('BackendServer', backref=backref('server_option', uselist=False))
    check = Column(TINYINT)
    check_inter = Column(VARCHAR)
    check_fall = Column(INT)
    cookie_value = Column(VARCHAR)



