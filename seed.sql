-- =====================================================================
-- STUDENT PLACEMENT DATA ANALYSIS SYSTEM
-- Synthetic Seed Data Script
-- NOTE: ALL DATA IN THIS FILE IS SYNTHETIC AND DESIGNED SOLELY FOR
-- COLLEGE PROJECT DEMONSTRATION AND TESTING PURPOSES.
-- =====================================================================

USE `placement_db`;

-- 1. Insert Default Administrative & Evaluation Users
INSERT INTO `users` (`username`, `password_hash`, `full_name`, `role`, `email`) VALUES
('admin', 'scrypt:32768:8:1$rrQgjYh4c73Ag8An$7be224f435f5687437724c1f496c3ec2f96c6565210d17aec70f08a7407af0312b42648711ad60878597ef5a0e366292d0183394becdf1cb8a8f8b4aec5f8226', 'System Administrator', 'admin', 'admin@placement.edu'),
('faculty', 'scrypt:32768:8:1$AnG7EoNiuIjC4odF$cff34249f2ff6dacb86da3cbc02d0cadbcb7ab0b6843abc0bcb3c60ff9848a456d4096172197d11e3f85eea32677e363a9931bbc353a2cb4d022cd97142f647b', 'Prof. Faculty Reviewer', 'placement_officer', 'faculty@placement.edu');

-- 2. Insert In-Demand Industry Skills Master
INSERT INTO `skills` (`skill_name`, `skill_category`) VALUES
('Python', 'Programming'),
('Java', 'Programming'),
('C++', 'Programming'),
('SQL', 'Database & Querying'),
('Data Structures & Algorithms', 'Core CS'),
('Machine Learning', 'AI/Data Science'),
('Deep Learning', 'AI/Data Science'),
('Natural Language Processing', 'AI/Data Science'),
('Computer Vision', 'AI/Data Science'),
('Flask / Web Frameworks', 'Web Development'),
('React.js', 'Web Development'),
('HTML/CSS/JavaScript', 'Web Development'),
('Cloud Computing (AWS/GCP)', 'DevOps & Cloud'),
('Docker & Kubernetes', 'DevOps & Cloud'),
('Embedded Systems', 'Core Engineering'),
('IoT & Microcontrollers', 'Core Engineering'),
('Problem Solving', 'Aptitude & Soft Skills'),
('Communication Skills', 'Aptitude & Soft Skills');

-- 3. Insert Partner Recruiting Companies
INSERT INTO `companies` (`company_name`, `industry`, `location`, `website`, `tier`) VALUES
('Google', 'Product / Technology', 'Hyderabad / Bangalore', 'https://careers.google.com', 'Super Dream'),
('Microsoft', 'Product / Cloud', 'Hyderabad / Bangalore', 'https://careers.microsoft.com', 'Super Dream'),
('Amazon', 'E-Commerce / Cloud', 'Hyderabad / Chennai', 'https://amazon.jobs', 'Super Dream'),
('Qualcomm', 'Semiconductors / Hardware', 'Bangalore / Chennai', 'https://qualcomm.com', 'Super Dream'),
('NVIDIA', 'AI Computing & Graphics', 'Pune / Bangalore', 'https://nvidia.com/careers', 'Super Dream'),
('Cisco Systems', 'Networking & Security', 'Bangalore', 'https://cisco.com', 'Dream'),
('Oracle', 'Enterprise Software & Cloud', 'Bangalore / Hyderabad', 'https://oracle.com', 'Dream'),
('Deloitte', 'Consulting & Analytics', 'Hyderabad / Mumbai', 'https://deloitte.com', 'Dream'),
('Tata Consultancy Services (TCS)', 'IT Services & Consulting', 'Pan India', 'https://tcs.com', 'Mass / IT Services'),
('Infosys', 'IT Services & Digital', 'Bangalore / Mysore', 'https://infosys.com', 'Mass / IT Services'),
('Wipro', 'IT Services', 'Bangalore / Hyderabad', 'https://wipro.com', 'Mass / IT Services'),
('Cognizant', 'Digital & Technology', 'Chennai / Coimbatore', 'https://cognizant.com', 'Mass / IT Services'),
('Accenture', 'Technology & Consulting', 'Bangalore / Chennai', 'https://accenture.com', 'Dream'),
('Bosch Global Software', 'Automotive & IoT', 'Bangalore / Coimbatore', 'https://bosch.in', 'Core Engineering'),
('L&T Technology Services', 'Engineering & R&D', 'Chennai / Mumbai', 'https://ltts.com', 'Core Engineering'),
('Tata Motors', 'Automotive Manufacturing', 'Pune / Jamshedpur', 'https://tatamotors.com', 'Core Engineering');

-- 4. Insert Students Across 6 Departments (Years: 2024, 2025, 2026)
-- Edge cases included: eligible placed, eligible unplaced, and ineligible students
INSERT INTO `students` (`student_id`, `roll_no`, `student_name`, `department`, `graduation_year`, `cgpa`, `email`, `phone`, `gender`, `eligible_for_placement`) VALUES
-- Computer Science and Engineering (CSE)
(1, '22BCE1001', 'Aarav Sharma', 'Computer Science and Engineering', 2026, 9.45, 'aarav.sharma@college.edu', '9876543210', 'Male', 1),
(2, '22BCE1002', 'Aditi Rao', 'Computer Science and Engineering', 2026, 9.12, 'aditi.rao@college.edu', '9876543211', 'Female', 1),
(3, '22BCE1003', 'Rohan Verma', 'Computer Science and Engineering', 2026, 8.75, 'rohan.verma@college.edu', '9876543212', 'Male', 1),
(4, '22BCE1004', 'Ananya Iyer', 'Computer Science and Engineering', 2026, 8.40, 'ananya.iyer@college.edu', '9876543213', 'Female', 1),
(5, '22BCE1005', 'Karthik N', 'Computer Science and Engineering', 2026, 7.85, 'karthik.n@college.edu', '9876543214', 'Male', 1),
(6, '22BCE1006', 'Sneha Patel', 'Computer Science and Engineering', 2026, 7.20, 'sneha.patel@college.edu', '9876543215', 'Female', 1),
(7, '22BCE1007', 'Vikramaditya S', 'Computer Science and Engineering', 2026, 6.45, 'vikram.s@college.edu', '9876543216', 'Male', 1),
(8, '22BCE1008', 'Meera Krishnan', 'Computer Science and Engineering', 2026, 5.80, 'meera.k@college.edu', '9876543217', 'Female', 0), -- Ineligible (CGPA < 6.0)
(9, '21BCE1010', 'Tanmay Joshi', 'Computer Science and Engineering', 2025, 9.20, 'tanmay.j@college.edu', '9876543218', 'Male', 1),
(10, '21BCE1011', 'Pooja Reddy', 'Computer Science and Engineering', 2025, 8.65, 'pooja.r@college.edu', '9876543219', 'Female', 1),
(11, '21BCE1012', 'Siddharth Nair', 'Computer Science and Engineering', 2025, 7.90, 'siddharth.n@college.edu', '9876543220', 'Male', 1),
(12, '20BCE1020', 'Varun Menon', 'Computer Science and Engineering', 2024, 8.80, 'varun.m@college.edu', '9876543221', 'Male', 1),

-- Artificial Intelligence and Machine Learning (AIML)
(13, '22AML1001', 'Diya Sundaram', 'Artificial Intelligence and Machine Learning', 2026, 9.60, 'diya.s@college.edu', '9876543222', 'Female', 1),
(14, '22AML1002', 'Pranav Kulkarni', 'Artificial Intelligence and Machine Learning', 2026, 9.25, 'pranav.k@college.edu', '9876543223', 'Male', 1),
(15, '22AML1003', 'Shruti Deshmukh', 'Artificial Intelligence and Machine Learning', 2026, 8.95, 'shruti.d@college.edu', '9876543224', 'Female', 1),
(16, '22AML1004', 'Harshavardhan R', 'Artificial Intelligence and Machine Learning', 2026, 8.50, 'harsha.r@college.edu', '9876543225', 'Male', 1),
(17, '22AML1005', 'Kavya Srinivasan', 'Artificial Intelligence and Machine Learning', 2026, 8.10, 'kavya.s@college.edu', '9876543226', 'Female', 1),
(18, '22AML1006', 'Nikhil Gupta', 'Artificial Intelligence and Machine Learning', 2026, 7.60, 'nikhil.g@college.edu', '9876543227', 'Male', 1),
(19, '22AML1007', 'Rhea Bansal', 'Artificial Intelligence and Machine Learning', 2026, 6.95, 'rhea.b@college.edu', '9876543228', 'Female', 1),
(20, '22AML1008', 'Abhinav Saxena', 'Artificial Intelligence and Machine Learning', 2026, 5.40, 'abhinav.s@college.edu', '9876543229', 'Male', 0), -- Ineligible
(21, '21AML1009', 'Nandini Chopra', 'Artificial Intelligence and Machine Learning', 2025, 9.05, 'nandini.c@college.edu', '9876543230', 'Female', 1),
(22, '21AML1010', 'Gautam Singhania', 'Artificial Intelligence and Machine Learning', 2025, 8.40, 'gautam.s@college.edu', '9876543231', 'Male', 1),
(23, '20AML1015', 'Arjun Pillai', 'Artificial Intelligence and Machine Learning', 2024, 8.70, 'arjun.p@college.edu', '9876543232', 'Male', 1),

-- Information Technology (IT)
(24, '22BIT1001', 'Ishaan Malhotra', 'Information Technology', 2026, 8.90, 'ishaan.m@college.edu', '9876543233', 'Male', 1),
(25, '22BIT1002', 'Ritu Agarwal', 'Information Technology', 2026, 8.60, 'ritu.a@college.edu', '9876543234', 'Female', 1),
(26, '22BIT1003', 'Vivek Pandey', 'Information Technology', 2026, 8.15, 'vivek.p@college.edu', '9876543235', 'Male', 1),
(27, '22BIT1004', 'Ananya Dutta', 'Information Technology', 2026, 7.70, 'ananya.d@college.edu', '9876543236', 'Female', 1),
(28, '22BIT1005', 'Rajeshwari M', 'Information Technology', 2026, 7.35, 'rajeshwari.m@college.edu', '9876543237', 'Female', 1),
(29, '22BIT1006', 'Akash Tripathi', 'Information Technology', 2026, 6.70, 'akash.t@college.edu', '9876543238', 'Male', 1),
(30, '21BIT1010', 'Bhavya Shah', 'Information Technology', 2025, 8.55, 'bhavya.s@college.edu', '9876543239', 'Female', 1),
(31, '21BIT1011', 'Devansh Rawat', 'Information Technology', 2025, 7.95, 'devansh.r@college.edu', '9876543240', 'Male', 1),
(32, '20BIT1015', 'Kunal Bhatia', 'Information Technology', 2024, 8.30, 'kunal.b@college.edu', '9876543241', 'Male', 1),

-- Electronics and Communication Engineering (ECE)
(33, '22ECE1001', 'Rahul Nambiar', 'Electronics and Communication Engineering', 2026, 9.30, 'rahul.n@college.edu', '9876543242', 'Male', 1),
(34, '22ECE1002', 'Swati Sen', 'Electronics and Communication Engineering', 2026, 8.85, 'swati.s@college.edu', '9876543243', 'Female', 1),
(35, '22ECE1003', 'Tarun Chawla', 'Electronics and Communication Engineering', 2026, 8.30, 'tarun.c@college.edu', '9876543244', 'Male', 1),
(36, '22ECE1004', 'Monika Das', 'Electronics and Communication Engineering', 2026, 7.80, 'monika.d@college.edu', '9876543245', 'Female', 1),
(37, '22ECE1005', 'Chetan Bhagat', 'Electronics and Communication Engineering', 2026, 7.15, 'chetan.b@college.edu', '9876543246', 'Male', 1),
(38, '22ECE1006', 'Deepa Jayaram', 'Electronics and Communication Engineering', 2026, 6.50, 'deepa.j@college.edu', '9876543247', 'Female', 1),
(39, '21ECE1008', 'Manoj Gowda', 'Electronics and Communication Engineering', 2025, 8.45, 'manoj.g@college.edu', '9876543248', 'Male', 1),
(40, '21ECE1009', 'Lavanya S', 'Electronics and Communication Engineering', 2025, 7.75, 'lavanya.s@college.edu', '9876543249', 'Female', 1),
(41, '20ECE1012', 'Pawan Kumar', 'Electronics and Communication Engineering', 2024, 8.10, 'pawan.k@college.edu', '9876543250', 'Male', 1),

-- Electrical and Electronics Engineering (EEE)
(42, '22EEE1001', 'Surya Prakash', 'Electrical and Electronics Engineering', 2026, 8.95, 'surya.p@college.edu', '9876543251', 'Male', 1),
(43, '22EEE1002', 'Nehal Jain', 'Electrical and Electronics Engineering', 2026, 8.40, 'nehal.j@college.edu', '9876543252', 'Female', 1),
(44, '22EEE1003', 'Aditya Madhavan', 'Electrical and Electronics Engineering', 2026, 7.90, 'aditya.m@college.edu', '9876543253', 'Male', 1),
(45, '22EEE1004', 'Priyanka Ghosh', 'Electrical and Electronics Engineering', 2026, 7.30, 'priyanka.g@college.edu', '9876543254', 'Female', 1),
(46, '22EEE1005', 'Ganesh Moorthy', 'Electrical and Electronics Engineering', 2026, 6.60, 'ganesh.m@college.edu', '9876543255', 'Male', 1),
(47, '21EEE1007', 'Harini Bala', 'Electrical and Electronics Engineering', 2025, 8.25, 'harini.b@college.edu', '9876543256', 'Female', 1),
(48, '21EEE1008', 'Kishore Varma', 'Electrical and Electronics Engineering', 2025, 7.50, 'kishore.v@college.edu', '9876543257', 'Male', 1),
(49, '20EEE1010', 'Dinesh Karthik', 'Electrical and Electronics Engineering', 2024, 7.85, 'dinesh.k@college.edu', '9876543258', 'Male', 1),

-- Mechanical Engineering (MECH)
(50, '22MEC1001', 'Rohit Chandran', 'Mechanical Engineering', 2026, 8.70, 'rohit.c@college.edu', '9876543259', 'Male', 1),
(51, '22MEC1002', 'Shalini Hegde', 'Mechanical Engineering', 2026, 8.20, 'shalini.h@college.edu', '9876543260', 'Female', 1),
(52, '22MEC1003', 'Vishnu Teja', 'Mechanical Engineering', 2026, 7.75, 'vishnu.t@college.edu', '9876543261', 'Male', 1),
(53, '22MEC1004', 'Suresh Balaji', 'Mechanical Engineering', 2026, 7.10, 'suresh.b@college.edu', '9876543262', 'Male', 1),
(54, '22MEC1005', 'Preeti Somani', 'Mechanical Engineering', 2026, 6.40, 'preeti.s@college.edu', '9876543263', 'Female', 1),
(55, '21MEC1007', 'Bharat Simha', 'Mechanical Engineering', 2025, 7.95, 'bharat.s@college.edu', '9876543264', 'Male', 1),
(56, '21MEC1008', 'Kavitha Natarajan', 'Mechanical Engineering', 2025, 7.30, 'kavitha.n@college.edu', '9876543265', 'Female', 1),
(57, '20MEC1010', 'Vinay Anand', 'Mechanical Engineering', 2024, 7.60, 'vinay.a@college.edu', '9876543266', 'Male', 1);

-- 5. Insert Student-Skill Associations
INSERT INTO `student_skills` (`student_id`, `skill_id`, `proficiency_level`) VALUES
-- CSE Top Students (Aarav, Aditi, Rohan, Ananya)
(1, 1, 'Advanced'), (1, 4, 'Advanced'), (1, 5, 'Advanced'), (1, 10, 'Intermediate'), (1, 13, 'Intermediate'),
(2, 1, 'Advanced'), (2, 2, 'Advanced'), (2, 4, 'Advanced'), (2, 5, 'Advanced'), (2, 17, 'Advanced'),
(3, 1, 'Intermediate'), (3, 4, 'Advanced'), (3, 5, 'Intermediate'), (3, 11, 'Advanced'), (3, 12, 'Advanced'),
(4, 2, 'Advanced'), (4, 4, 'Intermediate'), (4, 5, 'Intermediate'), (4, 18, 'Advanced'),
(5, 1, 'Intermediate'), (5, 4, 'Intermediate'), (5, 12, 'Advanced'),
(6, 4, 'Beginner'), (6, 12, 'Intermediate'), (6, 18, 'Intermediate'),
(7, 12, 'Beginner'), (7, 18, 'Beginner'),
(9, 1, 'Advanced'), (9, 4, 'Advanced'), (9, 5, 'Advanced'), (9, 14, 'Intermediate'),
(10, 2, 'Advanced'), (10, 4, 'Advanced'), (10, 5, 'Intermediate'),
(11, 4, 'Intermediate'), (11, 12, 'Intermediate'),
(12, 1, 'Advanced'), (12, 5, 'Advanced'), (12, 13, 'Advanced'),

-- AIML Students (Diya, Pranav, Shruti, Harsha)
(13, 1, 'Advanced'), (13, 4, 'Advanced'), (13, 5, 'Advanced'), (13, 6, 'Advanced'), (13, 7, 'Advanced'), (13, 8, 'Advanced'),
(14, 1, 'Advanced'), (14, 4, 'Advanced'), (14, 5, 'Advanced'), (14, 6, 'Advanced'), (14, 9, 'Advanced'),
(15, 1, 'Advanced'), (15, 4, 'Intermediate'), (15, 6, 'Advanced'), (15, 7, 'Intermediate'), (15, 10, 'Intermediate'),
(16, 1, 'Intermediate'), (16, 4, 'Intermediate'), (16, 6, 'Intermediate'), (16, 17, 'Advanced'),
(17, 1, 'Intermediate'), (17, 4, 'Intermediate'), (17, 18, 'Advanced'),
(18, 1, 'Beginner'), (18, 4, 'Beginner'), (18, 12, 'Intermediate'),
(19, 4, 'Beginner'), (19, 18, 'Intermediate'),
(21, 1, 'Advanced'), (21, 5, 'Advanced'), (21, 6, 'Advanced'), (21, 8, 'Intermediate'),
(22, 1, 'Intermediate'), (22, 4, 'Intermediate'), (22, 6, 'Intermediate'),
(23, 1, 'Advanced'), (23, 6, 'Advanced'), (23, 7, 'Advanced'),

-- IT Students
(24, 1, 'Advanced'), (24, 4, 'Advanced'), (24, 11, 'Advanced'), (24, 12, 'Advanced'),
(25, 2, 'Advanced'), (25, 4, 'Advanced'), (25, 5, 'Intermediate'), (25, 18, 'Advanced'),
(26, 1, 'Intermediate'), (26, 4, 'Intermediate'), (26, 10, 'Intermediate'),
(27, 4, 'Intermediate'), (27, 12, 'Intermediate'),
(28, 4, 'Beginner'), (28, 18, 'Intermediate'),
(30, 1, 'Advanced'), (30, 4, 'Advanced'), (30, 11, 'Advanced'),
(31, 2, 'Intermediate'), (31, 4, 'Intermediate'),
(32, 1, 'Advanced'), (32, 4, 'Advanced'), (32, 13, 'Intermediate'),

-- ECE Students
(33, 1, 'Intermediate'), (33, 3, 'Advanced'), (33, 5, 'Intermediate'), (33, 15, 'Advanced'), (33, 16, 'Advanced'),
(34, 1, 'Intermediate'), (34, 3, 'Advanced'), (34, 15, 'Advanced'), (34, 18, 'Advanced'),
(35, 1, 'Intermediate'), (35, 4, 'Intermediate'), (35, 16, 'Intermediate'),
(36, 4, 'Intermediate'), (36, 18, 'Intermediate'),
(39, 3, 'Advanced'), (39, 15, 'Advanced'),
(40, 1, 'Intermediate'), (40, 4, 'Intermediate'),
(41, 1, 'Advanced'), (41, 3, 'Advanced'), (41, 15, 'Advanced'),

-- EEE Students
(42, 1, 'Intermediate'), (42, 3, 'Intermediate'), (42, 15, 'Intermediate'), (42, 16, 'Advanced'),
(43, 1, 'Intermediate'), (43, 4, 'Intermediate'), (43, 16, 'Intermediate'),
(44, 4, 'Intermediate'), (44, 18, 'Intermediate'),
(47, 1, 'Intermediate'), (47, 16, 'Intermediate'),
(49, 1, 'Intermediate'), (49, 4, 'Intermediate'),

-- MECH Students
(50, 1, 'Intermediate'), (50, 17, 'Advanced'), (50, 18, 'Advanced'),
(51, 1, 'Beginner'), (51, 4, 'Intermediate'), (51, 17, 'Intermediate'),
(52, 17, 'Intermediate'), (52, 18, 'Intermediate'),
(55, 1, 'Intermediate'), (55, 17, 'Intermediate'),
(57, 18, 'Intermediate');

-- 6. Insert Placements (Job Offers with Package in LPA)
-- All packages are annual CTC in Lakhs Per Annum (INR).
INSERT INTO `placements` (`student_id`, `company_id`, `role`, `package_amount`, `package_unit`, `placement_date`, `placement_year`, `status`, `offer_type`, `notes`) VALUES
-- CSE Batch 2026 Placements
(1, 1, 'Associate Software Engineer', 32.50, 'LPA', '2025-09-15', 2026, 'Placed', 'Super Dream', 'Campus recruit - Google SWE'),
(1, 2, 'Software Development Engineer', 28.00, 'LPA', '2025-08-20', 2026, 'Offer Accepted', 'Super Dream', 'Accepted primary offer at Microsoft'),
(2, 2, 'Cloud Solutions Engineer', 24.50, 'LPA', '2025-09-10', 2026, 'Placed', 'Super Dream', 'Microsoft Azure core engineering'),
(3, 3, 'SDE - 1', 21.00, 'LPA', '2025-10-05', 2026, 'Placed', 'Super Dream', 'Amazon Web Services team'),
(4, 7, 'Applications Engineer', 14.50, 'LPA', '2025-11-02', 2026, 'Placed', 'Dream', 'Oracle Cloud Infrastructure'),
(5, 8, 'Technology Analyst', 9.50, 'LPA', '2025-11-20', 2026, 'Placed', 'Dream', 'Deloitte Consulting USI'),
(6, 9, 'Systems Engineer', 4.25, 'LPA', '2025-12-10', 2026, 'Placed', 'Mass / IT Services', 'TCS Ninja drive'),
(7, 10, 'Systems Associate', 3.80, 'LPA', '2026-01-15', 2026, 'Placed', 'Mass / IT Services', 'Infosys campus recruit'),

-- AIML Batch 2026 Placements
(13, 5, 'AI / Deep Learning Researcher', 42.00, 'LPA', '2025-09-01', 2026, 'Placed', 'Super Dream', 'NVIDIA LLM acceleration team'),
(13, 1, 'Machine Learning Engineer', 34.00, 'LPA', '2025-08-25', 2026, 'Offer Pending', 'Super Dream', 'Secondary high offer'),
(14, 1, 'Data & ML Engineer', 30.00, 'LPA', '2025-09-22', 2026, 'Placed', 'Super Dream', 'Google Brain / Research India'),
(15, 3, 'Data Scientist - GenAI', 23.50, 'LPA', '2025-10-18', 2026, 'Placed', 'Super Dream', 'Amazon Alexa / Search team'),
(16, 8, 'Data & AI Consultant', 10.00, 'LPA', '2025-11-12', 2026, 'Placed', 'Dream', 'Deloitte AI practice'),
(17, 13, 'Associate AI Developer', 8.50, 'LPA', '2025-11-28', 2026, 'Placed', 'Dream', 'Accenture Innovation Hub'),
(18, 12, 'Programmer Analyst', 4.50, 'LPA', '2026-01-10', 2026, 'Placed', 'Mass / IT Services', 'Cognizant GenC Next'),

-- IT Batch 2026 Placements
(24, 3, 'Full Stack Cloud Developer', 18.00, 'LPA', '2025-10-12', 2026, 'Placed', 'Super Dream', 'Amazon Retail team'),
(25, 6, 'Network Software Engineer', 16.00, 'LPA', '2025-10-25', 2026, 'Placed', 'Dream', 'Cisco Security & Cloud'),
(26, 7, 'Database Systems Engineer', 12.00, 'LPA', '2025-11-15', 2026, 'Placed', 'Dream', 'Oracle MySQL / DB team'),
(27, 13, 'Software Engineer Associate', 7.50, 'LPA', '2025-12-05', 2026, 'Placed', 'Dream', 'Accenture Advanced Technology'),
(28, 11, 'Project Engineer', 4.00, 'LPA', '2026-01-20', 2026, 'Placed', 'Mass / IT Services', 'Wipro Turbo drive'),

-- ECE Batch 2026 Placements
(33, 4, 'Silicon Validation Engineer', 22.00, 'LPA', '2025-09-18', 2026, 'Placed', 'Super Dream', 'Qualcomm Modem Systems'),
(34, 14, 'Embedded IoT Engineer', 11.50, 'LPA', '2025-11-05', 2026, 'Placed', 'Core Engineering', 'Bosch Connected Mobility'),
(35, 6, 'Embedded Systems Engineer', 13.00, 'LPA', '2025-11-25', 2026, 'Placed', 'Dream', 'Cisco Hardware engineering'),
(36, 9, 'Digital Associate', 4.00, 'LPA', '2026-01-12', 2026, 'Placed', 'Mass / IT Services', 'TCS Digital'),

-- EEE Batch 2026 Placements
(42, 14, 'Automotive Electronics Engineer', 10.50, 'LPA', '2025-11-18', 2026, 'Placed', 'Core Engineering', 'Bosch Powertrain Systems'),
(43, 15, 'Power Systems Engineer', 7.00, 'LPA', '2025-12-08', 2026, 'Placed', 'Core Engineering', 'L&T Technology Services'),
(44, 10, 'Software Analyst', 4.00, 'LPA', '2026-01-18', 2026, 'Placed', 'Mass / IT Services', 'Infosys Digital Specialist'),

-- MECH Batch 2026 Placements
(50, 16, 'Graduate Engineer Trainee - Design', 8.00, 'LPA', '2025-11-20', 2026, 'Placed', 'Core Engineering', 'Tata Motors EV Division'),
(51, 15, 'R&D Mechanical Engineer', 6.50, 'LPA', '2025-12-14', 2026, 'Placed', 'Core Engineering', 'L&T Defense & Aerospace'),
(52, 9, 'Assistant Engineer', 3.60, 'LPA', '2026-01-22', 2026, 'Placed', 'Mass / IT Services', 'TCS Engineering Services'),

-- Previous Years Placements (2025 & 2024 for Trend & Comparative Analysis)
(9, 1, 'Software Engineer', 28.00, 'LPA', '2024-09-12', 2025, 'Placed', 'Super Dream', 'Google SWE Batch 2025'),
(10, 2, 'Software Engineer', 22.00, 'LPA', '2024-09-20', 2025, 'Placed', 'Super Dream', 'Microsoft Batch 2025'),
(11, 9, 'Systems Engineer', 4.00, 'LPA', '2024-11-15', 2025, 'Placed', 'Mass / IT Services', 'TCS Batch 2025'),
(21, 5, 'AI Engineer', 36.00, 'LPA', '2024-09-08', 2025, 'Placed', 'Super Dream', 'NVIDIA Batch 2025'),
(22, 8, 'Data Analyst', 9.00, 'LPA', '2024-10-18', 2025, 'Placed', 'Dream', 'Deloitte Batch 2025'),
(30, 3, 'Cloud Engineer', 16.50, 'LPA', '2024-10-02', 2025, 'Placed', 'Dream', 'Amazon Batch 2025'),
(31, 10, 'Software Engineer', 4.00, 'LPA', '2024-11-20', 2025, 'Placed', 'Mass / IT Services', 'Infosys Batch 2025'),
(39, 4, 'Hardware Engineer', 19.50, 'LPA', '2024-10-15', 2025, 'Placed', 'Super Dream', 'Qualcomm Batch 2025'),
(40, 12, 'Engineer Associate', 4.20, 'LPA', '2024-12-05', 2025, 'Placed', 'Mass / IT Services', 'Cognizant Batch 2025'),
(47, 14, 'Control Systems Engineer', 9.00, 'LPA', '2024-11-12', 2025, 'Placed', 'Core Engineering', 'Bosch Batch 2025'),
(48, 9, 'Graduate Trainee', 3.80, 'LPA', '2024-12-20', 2025, 'Placed', 'Mass / IT Services', 'TCS Batch 2025'),
(55, 16, 'GET - Vehicle Dynamics', 7.50, 'LPA', '2024-11-18', 2025, 'Placed', 'Core Engineering', 'Tata Motors Batch 2025'),
(56, 15, 'Design Trainee', 6.00, 'LPA', '2024-12-15', 2025, 'Placed', 'Core Engineering', 'L&T Batch 2025'),

-- Batch 2024
(12, 2, 'Software Engineer', 20.00, 'LPA', '2023-09-15', 2024, 'Placed', 'Super Dream', 'Microsoft Batch 2024'),
(23, 1, 'Data Scientist', 26.00, 'LPA', '2023-09-28', 2024, 'Placed', 'Super Dream', 'Google Batch 2024'),
(32, 7, 'Applications Engineer', 11.00, 'LPA', '2023-10-20', 2024, 'Placed', 'Dream', 'Oracle Batch 2024'),
(41, 4, 'ASIC Design Engineer', 18.00, 'LPA', '2023-10-12', 2024, 'Placed', 'Super Dream', 'Qualcomm Batch 2024'),
(49, 14, 'Electrical Trainee', 8.50, 'LPA', '2023-11-22', 2024, 'Placed', 'Core Engineering', 'Bosch Batch 2024'),
(57, 16, 'Plant Engineer Trainee', 7.00, 'LPA', '2023-11-10', 2024, 'Placed', 'Core Engineering', 'Tata Motors Batch 2024');
