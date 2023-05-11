CREATE TABLE scylla (
    id CHAR(20) NOT NULL,
    port INT(10) not null default '0',
    name char(20) not null DEFAULT '',
    proxy_type CHAR(10) not null DEFAULT '',
    is_cn SMALLINT(2) not null default '0',
    country CHAR(10) not null DEFAULT '',
    uptime INT(10) not null default '0',
    speed INT(10) not null default '0',
    status SMALLINT(2) not null default '0',
    check_count SMALLINT(2) not null default '0',
    fail_count SMALLINT(2) not null default '0',
    last_time datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY(id),
    KEY idx_last_time(last_time),
    KEY idx_status(status),
    KEY idx_proxy_type(proxy_type),
    KEY idx_country(country)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;