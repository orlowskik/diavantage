INSERT INTO diaweb_address (number, street, city, state, zip_code, country)
VALUES (123, 'Elm Street', 'Springfield', 'IL', '62704', 'USA'),
       (456, 'Oak Avenue', 'Springfield', 'IL', '62705', 'USA'),
       (789, 'Pine Road', 'Springfield', 'IL', '62706', 'USA'),
       (135, 'Maple Drive', 'Springfield', 'IL', '62707', 'USA'),
       (246, 'Birch Lane', 'Springfield', 'IL', '62708', 'USA'),
       (357, 'Cedar Street', 'Springfield', 'IL', '62709', 'USA'),
       (468, 'Dogwood Blvd', 'Springfield', 'IL', '62710', 'USA'),
       (579, 'Elmwood Court', 'Springfield', 'IL', '62711', 'USA'),
       (680, 'Fir Place', 'Springfield', 'IL', '62712', 'USA'),
       (791, 'Grove Ave', 'Springfield', 'IL', '62713', 'USA'),
       (802, 'Hemlock Rd', 'Springfield', 'IL', '62714', 'USA'),
       (913, 'Ivy Street', 'Springfield', 'IL', '62715', 'USA');



INSERT INTO auth_user (username, first_name, last_name, email, password, is_staff, is_active, date_joined, is_superuser)
VALUES ('jdoe', 'John', 'Doe', 'johndoe@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('asmith', 'Alice', 'Smith', 'alicesmith@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('bjohnson', 'Bob', 'Johnson', 'bobjohnson@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('cmiller', 'Carol', 'Miller', 'carolmiller@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('ddavis', 'David', 'Davis', 'daviddavis@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('edwards', 'Eve', 'Edwards', 'eveedwards@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('ffrancis', 'Frank', 'Francis', 'frankfrancis@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('ggarcia', 'Grace', 'Garcia', 'gracegarcia@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('hharris', 'Harry', 'Harris', 'harryharris@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('ijefferson', 'Ivy', 'Jefferson', 'ivyjefferson@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('kking', 'Kate', 'King', 'kateking@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('lmorris', 'Laura', 'Morris', 'lauramorris@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('nperez', 'Nina', 'Perez', 'ninaperez@example.com', 'password123', 0, 1, '2024-01-01', 0),
       ('owilson', 'Oscar', 'Wilson', 'oscarwilson@example.com', 'password123', 0, 1, '2024-01-01', 0);



INSERT INTO diaweb_physician (user_id, specialty, phone)
VALUES (1, 'Cardiology', '123-456-7890'),
       (2, 'Dermatology', '234-567-8901'),
       (3, 'Neurology', '345-678-9012'),
       (4, 'Pediatrics', '456-789-0123');


UPDATE diaweb_physician
SET address_id = 1
WHERE user_id IN (1, 2);

UPDATE diaweb_physician
SET address_id = 2
WHERE user_id IN (3, 4);


INSERT INTO diaweb_patient (user_id, birthdate, sex, classifier_result, confirmed_diabetes, address_id)
VALUES (5, '1980-05-23', 'M', 0, False, 3),
       (6, '1992-11-12', 'F', 0, False, 4),
       (7, '1978-07-30', 'M', 0, False, 5),
       (8, '1985-03-14', 'F', 0, False, 6),
       (9, '1990-09-27', 'M', 0, False, 7),
       (10, '1975-04-05', 'F', 0, False, 8),
       (11, '1988-12-19', 'M', 0, False, 9),
       (12, '1983-01-22', 'F', 0, False, 10),
       (13, '1995-06-15', 'M', 0, False, 11),
       (14, '1982-08-28', 'F', 0, False, 12);


INSERT INTO diaweb_physician_patient (physician_id, patient_id)
VALUES (1, 1),
       (1, 2),
       (2, 3),
       (2, 4),
       (3, 5),
       (3, 6),
       (4, 7),
       (4, 8),
       (1, 9),
       (1, 10);

