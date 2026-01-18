-- Database Creation Script
-- Run this FIRST before running any table migrations
-- This creates the users_db database that all services use

CREATE DATABASE IF NOT EXISTS users_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Grant permissions to the application user
-- (Adjust username/password as needed)
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'%' IDENTIFIED BY 'flaskpass';
GRANT ALL PRIVILEGES ON users_db.* TO 'flaskuser'@'localhost' IDENTIFIED BY 'flaskpass';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Use the database for subsequent operations
USE users_db;