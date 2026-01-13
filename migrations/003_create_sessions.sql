-- Migration: Create sessions table (optional, for session persistence)
-- Description: Stores JWT token metadata for session management

CREATE TABLE IF NOT EXISTS sessions (
    token_id VARCHAR(255) PRIMARY KEY,
    user_id INT NOT NULL,
    token_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_revoked (is_revoked)
);
