-- CREATE TABLE enrollment (enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES Users(user_id), FOREIGN KEY (course_id) REFERENCES courses(course_id));


-- INSERT INTO enrollment (user_id, course_id)
-- VALUES (2, 2);

SELECT * FROM enrollment;
