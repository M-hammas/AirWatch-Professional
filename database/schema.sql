CREATE DATABASE IF NOT EXISTS airwatch CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE airwatch;

-- The application creates the same tables through SQLAlchemy on first startup.
-- This SQL reference documents the relational structure for your DBMS demonstration.

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL
);

CREATE TABLE cities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  country VARCHAR(120) NOT NULL DEFAULT '',
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  timezone VARCHAR(80) NOT NULL DEFAULT 'UTC',
  UNIQUE KEY uq_city_coordinates (name, country, latitude, longitude)
);

CREATE TABLE monitoring_locations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  city_id INT NOT NULL,
  label VARCHAR(160) NOT NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

CREATE TABLE pollutants (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(20) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  unit VARCHAR(30) NOT NULL DEFAULT 'µg/m³'
);

CREATE TABLE air_quality_readings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id INT NOT NULL,
  recorded_at DATETIME NOT NULL,
  source VARCHAR(60) NOT NULL DEFAULT 'Open-Meteo',
  FOREIGN KEY (location_id) REFERENCES monitoring_locations(id) ON DELETE CASCADE,
  INDEX idx_location_recorded (location_id, recorded_at)
);

CREATE TABLE pollutant_values (
  id INT AUTO_INCREMENT PRIMARY KEY,
  reading_id INT NOT NULL,
  pollutant_id INT NOT NULL,
  value DOUBLE NOT NULL,
  UNIQUE KEY uq_reading_pollutant (reading_id, pollutant_id),
  FOREIGN KEY (reading_id) REFERENCES air_quality_readings(id) ON DELETE CASCADE,
  FOREIGN KEY (pollutant_id) REFERENCES pollutants(id)
);

CREATE TABLE alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  pollutant_code VARCHAR(20) NOT NULL,
  threshold DOUBLE NOT NULL,
  enabled TINYINT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE saved_locations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  location_id INT NOT NULL,
  created_at DATETIME NOT NULL,
  UNIQUE KEY uq_user_saved_location (user_id, location_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (location_id) REFERENCES monitoring_locations(id) ON DELETE CASCADE
);
