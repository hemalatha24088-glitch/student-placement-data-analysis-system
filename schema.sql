-- =====================================================================
-- STUDENT PLACEMENT DATA ANALYSIS SYSTEM
-- Database Schema Definition (MySQL 8.0+)
-- Database: placement_db
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `placement_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `placement_db`;

-- Drop existing tables in reverse foreign key order if needed
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `student_skills`;
DROP TABLE IF EXISTS `placements`;
DROP TABLE IF EXISTS `skills`;
DROP TABLE IF EXISTS `companies`;
DROP TABLE IF EXISTS `students`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------
-- Table 1: students
-- Stores core academic and personal records of students.
-- ---------------------------------------------------------------------
CREATE TABLE `students` (
    `student_id` INT AUTO_INCREMENT PRIMARY KEY,
    `roll_no` VARCHAR(50) NOT NULL UNIQUE,
    `student_name` VARCHAR(100) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `graduation_year` INT NOT NULL,
    `cgpa` DECIMAL(4, 2) DEFAULT NULL,
    `email` VARCHAR(120) DEFAULT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `gender` VARCHAR(20) DEFAULT 'Other',
    `eligible_for_placement` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_students_department` (`department`),
    INDEX `idx_students_grad_year` (`graduation_year`),
    INDEX `idx_students_eligibility` (`eligible_for_placement`),
    INDEX `idx_students_cgpa` (`cgpa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Table 2: skills
-- Master list of technical and soft skills evaluated in campus drives.
-- ---------------------------------------------------------------------
CREATE TABLE `skills` (
    `skill_id` INT AUTO_INCREMENT PRIMARY KEY,
    `skill_name` VARCHAR(100) NOT NULL UNIQUE,
    `skill_category` VARCHAR(50) NOT NULL DEFAULT 'Technical',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_skills_category` (`skill_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Table 3: student_skills (Bridge / Associative Entity)
-- Represents many-to-many relationship between students and skills.
-- ---------------------------------------------------------------------
CREATE TABLE `student_skills` (
    `student_id` INT NOT NULL,
    `skill_id` INT NOT NULL,
    `proficiency_level` VARCHAR(30) DEFAULT 'Intermediate',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`student_id`, `skill_id`),
    CONSTRAINT `fk_student_skills_student` 
        FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_student_skills_skill` 
        FOREIGN KEY (`skill_id`) REFERENCES `skills` (`skill_id`) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Table 4: companies
-- Stores recruiting partner company information and sectors.
-- ---------------------------------------------------------------------
CREATE TABLE `companies` (
    `company_id` INT AUTO_INCREMENT PRIMARY KEY,
    `company_name` VARCHAR(150) NOT NULL UNIQUE,
    `industry` VARCHAR(100) NOT NULL DEFAULT 'Information Technology',
    `location` VARCHAR(100) DEFAULT 'India',
    `website` VARCHAR(200) DEFAULT NULL,
    `tier` VARCHAR(50) DEFAULT 'Core / Product',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_companies_industry` (`industry`),
    INDEX `idx_companies_tier` (`tier`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Table 5: placements
-- Tracks job offers, roles, CTC packages (in LPA), dates, and statuses.
-- ---------------------------------------------------------------------
CREATE TABLE `placements` (
    `placement_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `company_id` INT NOT NULL,
    `role` VARCHAR(100) NOT NULL,
    `package_amount` DECIMAL(6, 2) NOT NULL,
    `package_unit` VARCHAR(20) NOT NULL DEFAULT 'LPA',
    `placement_date` DATE NOT NULL,
    `placement_year` INT NOT NULL,
    `status` VARCHAR(50) NOT NULL DEFAULT 'Placed',
    `offer_type` VARCHAR(50) DEFAULT 'Full-time',
    `notes` VARCHAR(255) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_placements_student` 
        FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_placements_company` 
        FOREIGN KEY (`company_id`) REFERENCES `companies` (`company_id`) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_placements_status` (`status`),
    INDEX `idx_placements_year` (`placement_year`),
    INDEX `idx_placements_package` (`package_amount`),
    INDEX `idx_placements_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Table 6: users (System administrators & Placement officers)
-- Enables role-based authentication and secure session management.
-- ---------------------------------------------------------------------
CREATE TABLE `users` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `role` VARCHAR(30) NOT NULL DEFAULT 'admin',
    `email` VARCHAR(120) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
