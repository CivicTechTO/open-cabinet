set timezone to 'UTC';

create function lastmod() returns trigger as $$
begin
  new.mod_time := NOW();
  return new;
end;
$$ LANGUAGE PLPGSQL;

CREATE TABLE orders(
   ID             INT,
   ORDER_COUNT    INT default 1,
   PUB_DATE       DATE,
   SUBJECT        VARCHAR(700),
   PRECIS         TEXT,
   CHAPTER        VARCHAR(100),
   BILL           VARCHAR(100),
   REG_ID         VARCHAR(30),
   REG_DATE       VARCHAR(30),
   URL            VARCHAR(250) NOT NULL,
   ADD_TIME       timestamptz default current_timestamp,
   MOD_TIME       timestamptz default current_timestamp,
   PRIMARY KEY( ID, ORDER_COUNT )
);

CREATE index on orders(PUB_DATE);

CREATE TABLE departments(
    ORDER_ID       INT NOT NULL,
    ORDER_COUNT    INT DEFAULT 1,
    DEPARTMENT     VARCHAR(30),
    ADD_TIME       timestamptz default current_timestamp,
    MOD_TIME       timestamptz default current_timestamp,
    PRIMARY KEY(ORDER_ID, ORDER_COUNT, DEPARTMENT),
    FOREIGN KEY (ORDER_ID, ORDER_COUNT) REFERENCES orders(id, order_count)
);

CREATE TRIGGER lastmod BEFORE UPDATE ON departments FOR EACH ROW EXECUTE PROCEDURE lastmod();
CREATE index on departments(order_id, order_count);


CREATE TABLE acts(
    ORDER_ID       INT NOT NULL,
    ORDER_COUNT    INT DEFAULT 1,
    ACT            VARCHAR(600),
    ADD_TIME       timestamptz default current_timestamp,
    MOD_TIME       timestamptz default current_timestamp,
    PRIMARY KEY(ORDER_ID, ORDER_COUNT, ACT),
    FOREIGN KEY (ORDER_ID, ORDER_COUNT) REFERENCES orders(ID, ORDER_COUNT)    
);

CREATE TRIGGER lastmod BEFORE UPDATE ON acts FOR EACH ROW EXECUTE PROCEDURE lastmod();
CREATE index on acts (order_id, order_count);


CREATE TABLE attachments(
   ID             BIGSERIAL PRIMARY KEY, 
   ORDER_ID       INT NOT NULL,
   ORDER_COUNT    INT DEFAULT 1,
   ATTACHMENT     TEXT,
   URL            VARCHAR(300) NOT NULL,
   ADD_TIME       timestamptz default current_timestamp,
   MOD_TIME       timestamptz default current_timestamp,
   UNIQUE( URL ),
   FOREIGN KEY (ORDER_ID, ORDER_COUNT) REFERENCES orders(ID, ORDER_COUNT)    
);

CREATE TRIGGER lastmod BEFORE UPDATE ON attachments FOR EACH ROW EXECUTE PROCEDURE lastmod();
CREATE index on attachments (order_id);


CREATE TABLE missing(
  ORDER_ID       INT NOT NULL,
  ADD_TIME       timestamptz default current_timestamp,
  MOD_TIME       timestamptz default current_timestamp,
  UNIQUE(ORDER_ID)
);

CREATE TRIGGER lastmod BEFORE UPDATE ON missing FOR EACH ROW EXECUTE PROCEDURE lastmod();

CREATE TABLE users(
  EMAIL         VARCHAR(200) PRIMARY KEY,
  CONFIRMATION   INT DEFAULT 0,
  ADD_TIME       timestamptz default current_timestamp,
  MOD_TIME       timestamptz default current_timestamp
);

CREATE TRIGGER lastmod BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE lastmod();
