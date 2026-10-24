-- Migration 001: Initial Core Schema
-- Creates students, companies, skills, placements, users, and student_skills

CREATE TABLE IF NOT EXISTS `schema_migrations` (
    `version` VARCHAR(100) PRIMARY KEY,
    `applied_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `users` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `role` ENUM('admin', 'placement_officer', 'student') NOT NULL DEFAULT 'student',
    `email` VARCHAR(120) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `students` (
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

CREATE TABLE IF NOT EXISTS `companies` (
    `company_id` INT AUTO_INCREMENT PRIMARY KEY,
    `company_name` VARCHAR(100) NOT NULL UNIQUE,
    `industry` VARCHAR(100) DEFAULT NULL,
    `location` VARCHAR(100) DEFAULT NULL,
    `tier` VARCHAR(50) DEFAULT 'Mass Recruit',
    `website` VARCHAR(200) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_companies_industry` (`industry`),
    INDEX `idx_companies_tier` (`tier`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `skills` (
    `skill_id` INT AUTO_INCREMENT PRIMARY KEY,
    `skill_name` VARCHAR(100) NOT NULL UNIQUE,
    `skill_category` VARCHAR(50) DEFAULT 'Technical',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_skills_category` (`skill_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `placements` (
    `placement_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `company_id` INT NOT NULL,
    `role` VARCHAR(100) NOT NULL,
    `package_amount` DECIMAL(6, 2) NOT NULL,
    `package_unit` VARCHAR(10) DEFAULT 'LPA',
    `placement_date` DATE DEFAULT NULL,
    `placement_year` INT NOT NULL,
    `status` ENUM('Placed', 'Offer Accepted', 'Offer Pending', 'Rejected') NOT NULL DEFAULT 'Placed',
    `offer_type` VARCHAR(50) DEFAULT 'Full-time',
    `notes` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE,
    FOREIGN KEY (`company_id`) REFERENCES `companies` (`company_id`) ON DELETE CASCADE,
    UNIQUE KEY `uq_student_company_year` (`student_id`, `company_id`, `role`, `placement_year`),
    INDEX `idx_placements_year` (`placement_year`),
    INDEX `idx_placements_status` (`status`),
    INDEX `idx_placements_package` (`package_amount`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `student_skills` (
    `student_id` INT NOT NULL,
    `skill_id` INT NOT NULL,
    PRIMARY KEY (`student_id`, `skill_id`),
    FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE,
    FOREIGN KEY (`skill_id`) REFERENCES `skills` (`skill_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
