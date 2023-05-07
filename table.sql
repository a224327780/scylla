CREATE TABLE IF NOT EXISTS scylla (
  id char(10) NOT NULL PRIMARY KEY,
  port smallint(4) not null default '0',
	name char(20) not null DEFAULT '',
	proxy_type char(10) not null DEFAULT '',
	is_cn INTEGER not null default '0',
	country char(10) not null DEFAULT '',
	uptime int(10) not null default '0',
	speed int(10) not null default '0',
	status smallint(2) not null default '0',
	check_count smallint(2) not null default '0',
	fail_count smallint(2) not null default '0',
	last_time char(20) not null DEFAULT ''
);
CREATE INDEX idx_last_time ON scylla (last_time);
CREATE INDEX idx_status ON scylla (status);