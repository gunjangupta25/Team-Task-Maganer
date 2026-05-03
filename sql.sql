CREATE DATABASE taskdb;
USE taskdb;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  password VARCHAR(255),
  role ENUM('admin','member') DEFAULT 'member'
);

DROP TABLE IF EXISTS tasks;

CREATE TABLE tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255),
  status ENUM('todo','done') DEFAULT 'todo',
  assigned_to INT,
  created_by INT,
  FOREIGN KEY (assigned_to) REFERENCES users(id)
);
USE taskdb;
SELECT * FROM users;
