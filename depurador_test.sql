-- Script de prueba para el depurador de datos
CREATE DATABASE IF NOT EXISTS depurador_test;
USE depurador_test;

DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    email VARCHAR(100),
    edad INT,
    ciudad VARCHAR(50)
);

INSERT INTO clientes (nombre, email, edad, ciudad) VALUES
('Ana Torres', 'ana@example.com', 25, 'Bogotá'),
('Luis Pérez', 'luis@example.com', 30, 'Cali'),
('Carlos Gómez', NULL, 22, 'Medellín'),         
('Marta Díaz', 'marta@example.com', NULL, 'Neiva'),
('Ana Torres', 'ana@example.com', 25, 'Bogotá');
