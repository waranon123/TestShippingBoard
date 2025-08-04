-- Create trucks table
CREATE TABLE trucks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    terminal VARCHAR(50) NOT NULL,
    truck_no VARCHAR(50) NOT NULL,
    dock_code VARCHAR(50) NOT NULL,
    truck_route VARCHAR(100) NOT NULL,
    preparation_start TIME,
    preparation_end TIME,
    loading_start TIME,
    loading_end TIME,
    status_preparation VARCHAR(20) DEFAULT 'On Process',
    status_loading VARCHAR(20) DEFAULT 'On Process',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX idx_truck_no ON trucks(truck_no);
CREATE INDEX idx_terminal ON trucks(terminal);
CREATE INDEX idx_status ON trucks(status_preparation, status_loading);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password_hash, role) 
VALUES ('admin', '$2b$12$YIuGqJKxVQK7K.KZqKHqeOC9Z7S9bXmX5LxGKVGQfPJjV9TvKqEly', 'admin');