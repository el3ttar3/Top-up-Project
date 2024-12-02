-- CREATE TABLE feedback (feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,course_id INTEGER NOT NULL,user_id INTEGER NOT NULL,                       
--     feedback TEXT,                                
--     FOREIGN KEY (course_id) REFERENCES courses(course_id),  
--     FOREIGN KEY (user_id) REFERENCES Users(user_id)        
-- );


-- INSERT INTO feedback (course_id, user_id, feedback)
-- VALUES (2, 2, 'Amazing course, learned a lot!');

SELECT * FROM feedback;