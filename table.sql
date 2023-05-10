CREATE TABLE IF NOT EXISTS scylla (
    id char(20) NOT NULL,
    port smallint(4) not null default '0',
    name char(20) not null DEFAULT '',
    proxy_type char(10) not null DEFAULT '',
    is_cn smallint(2) not null default '0',
    country char(10) not null DEFAULT '',
    uptime int(10) not null default '0',
    speed int(10) not null default '0',
    status smallint(2) not null default '0',
    check_count smallint(2) not null default '0',
    fail_count smallint(2) not null default '0',
    last_time datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY(id),
    KEY idx_last_time(last_time),
    KEY idx_status(status),
    KEY idx_proxy_type(proxy_type),
    KEY idx_country(country)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;