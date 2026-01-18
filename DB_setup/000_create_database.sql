-- Database Creation Script
-- Run this FIRST before running any table migrations
-- This creates the users_db database that all services use

CREATE DATABASE IF NOT EXISTS users_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create the application user (if not exists)
-- Note: MySQL 5.7+ supports CREATE USER IF NOT EXISTS
CREATE USER IF NOT EXISTS 'flaskuser'@'%' IDENTIFIED BY 'flaskpass';

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Use the database for subsequent operations
USE users_db;