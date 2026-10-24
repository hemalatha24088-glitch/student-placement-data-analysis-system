-- Migration 002: Add performance indexes and integrity constraints

-- Add composite index on student roll_no and email for authentication Lookups
CREATE INDEX `idx_users_username_email` ON `users` (`username`, `email`);

-- Ensure student skills index for quick gap analysis join
CREATE INDEX `idx_student_skills_skill` ON `student_skills` (`skill_id`);
