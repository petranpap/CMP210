CREATE DATABASE IF NOT EXISTS library_demo;
USE library_demo;

CREATE TABLE IF NOT EXISTS authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    nationality VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INT,
    genre VARCHAR(50),
    available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (author_id) REFERENCES authors(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

INSERT INTO authors (name, nationality) VALUES
('George Orwell', 'British'),
('Frank Herbert', 'American'),
('Robert Martin', 'American');

INSERT INTO books (title, author_id, genre) VALUES
('1984', 1, 'Dystopia'),
('Dune', 2, 'Sci-Fi'),
('Clean Code', 3, 'Programming');