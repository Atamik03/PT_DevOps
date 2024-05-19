CREATE USER repl_user WITH REPLICATION LOGIN PASSWORD '12345';

SELECT pg_create_physical_replication_slot('replication_slot');

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pt_bot') THEN
        CREATE DATABASE pt_bot;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS email(
    id SERIAL PRIMARY KEY,
    email VARCHAR(255)
);

INSERT INTO email (email) VALUES ('test1@email.ru'), ('test2@example.com');
INSERT INTO phone_numbers (phone_number) VALUES ('8 (987) 653-21-23'), ('8 (900) 202-00-12');

CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD '12345';

SELECT pg_create_physical_replication_slot('replication_slot');