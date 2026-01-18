-- Migration: Create admin_users table
-- Description: Separates admin credentials from regular users

CREATE TABLE IF NOT EXISTS admin_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username)
);

-- Insert default admin user (password should be hashed in production)
-- Default: admin / admin_password_hash
INSERT IGNORE INTO admin_users (username, password_hash, is_active) 
VALUES ('admin', 'scrypt:32768:8:1$jZEXQXNY5v5XSXMG$8f0f1e8c8f3f3c5b5e5a5f5c5e5a5f5c5e5a5f5c5e5a5f5c5e5a5f5c5e5a5f', TRUE);
