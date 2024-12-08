import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("school_management.db")
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    class TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    questions TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS test_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    test_id INTEGER,
    score INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(test_id) REFERENCES tests(id)
)
''')

conn.commit()

import customtkinter as ctk


class SchoolManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("800x500")

        # Main Frame
        self.frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Title
        self.title_label = ctk.CTkLabel(self.frame, text="School Management System", font=("Arial", 24))
        self.title_label.pack(pady=20)

        # Buttons
        self.register_btn = ctk.CTkButton(self.frame, text="Register Student", command=self.register_student)
        self.register_btn.pack(pady=10)

        self.view_students_btn = ctk.CTkButton(self.frame, text="View Students", command=self.view_students)
        self.view_students_btn.pack(pady=10)

        self.add_test_btn = ctk.CTkButton(self.frame, text="Add Test", command=self.add_test)
        self.add_test_btn.pack(pady=10)

        self.take_test_btn = ctk.CTkButton(self.frame, text="Take Test", command=self.take_test)
        self.take_test_btn.pack(pady=10)

        self.view_results_btn = ctk.CTkButton(self.frame, text="View Results", command=self.view_results)
        self.view_results_btn.pack(pady=10)

    def register_student(self):
        StudentRegistrationWindow(self.root)

    def view_students(self):
        ViewStudentsWindow(self.root)

    def add_test(self):
        AddTestWindow(self.root)

    def take_test(self):
        TakeTestWindow(self.root)

    def view_results(self):
        ResultsViewerWindow(self.root)


class StudentRegistrationWindow:
    def __init__(self, root):
        self.window = ctk.CTkToplevel(root)
        self.window.title("Register Student")
        self.window.geometry("400x300")

        # Input Fields
        ctk.CTkLabel(self.window, text="Name:").pack(pady=5)
        self.name_entry = ctk.CTkEntry(self.window, placeholder_text="Enter Name")
        self.name_entry.pack(pady=5)

        ctk.CTkLabel(self.window, text="Email:").pack(pady=5)
        self.email_entry = ctk.CTkEntry(self.window, placeholder_text="Enter Email")
        self.email_entry.pack(pady=5)

        ctk.CTkLabel(self.window, text="Class:").pack(pady=5)
        self.class_entry = ctk.CTkEntry(self.window, placeholder_text="Enter Class")
        self.class_entry.pack(pady=5)

        # Register Button
        self.register_btn = ctk.CTkButton(self.window, text="Register", command=self.register)
        self.register_btn.pack(pady=20)

    def register(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        student_class = self.class_entry.get()

        if not name or not email or not student_class:
            ctk.messagebox.showerror("Error", "All fields are required!")
            return

        try:
            cursor.execute("INSERT INTO students (name, email, class) VALUES (?, ?, ?)", (name, email, student_class))
            conn.commit()
            ctk.messagebox.showinfo("Success", "Student registered successfully!")
            self.window.destroy()
        except sqlite3.IntegrityError:
            ctk.messagebox.showerror("Error", "Student with this email already exists!")

class ViewStudentsWindow:
    def __init__(self, root):
        self.window = ctk.CTkToplevel(root)
        self.window.title("View Students")
        self.window.geometry("500x400")

        # Fetch Students
        students = cursor.execute("SELECT * FROM students").fetchall()

        if students:
            for student in students:
                student_info = f"ID: {student[0]}, Name: {student[1]}, Email: {student[2]}, Class: {student[3]}"
                ctk.CTkLabel(self.window, text=student_info).pack(pady=5)
        else:
            ctk.CTkLabel(self.window, text="No students found!").pack(pady=20)

import json

class AddTestWindow:
    def __init__(self, root):
        self.window = ctk.CTkToplevel(root)
        self.window.title("Add Test")
        self.window.geometry("400x400")

        ctk.CTkLabel(self.window, text="Test Title:").pack(pady=5)
        self.title_entry = ctk.CTkEntry(self.window, placeholder_text="Enter Test Title")
        self.title_entry.pack(pady=5)

        ctk.CTkLabel(self.window, text="Questions (Format: Question=Answer)").pack(pady=5)
        self.questions_entry = ctk.CTkTextbox(self.window, height=200)
        self.questions_entry.pack(pady=10)

        self.add_btn = ctk.CTkButton(self.window, text="Add Test", command=self.add_test)
        self.add_btn.pack(pady=10)

    def add_test(self):
        title = self.title_entry.get()
        questions_text = self.questions_entry.get("1.0", "end").strip()
        questions = {}

        for line in questions_text.split("\n"):
            if "=" in line:
                question, answer = line.split("=", 1)
                questions[question.strip()] = answer.strip()

        if not title or not questions:
            ctk.messagebox.showerror("Error", "All fields are required!")
            return

        questions_json = json.dumps(questions)
        cursor.execute("INSERT INTO tests (title, questions) VALUES (?, ?)", (title, questions_json))
        conn.commit()
        ctk.messagebox.showinfo("Success", "Test added successfully!")
        self.window.destroy()


class TakeTestWindow:
    def __init__(self, root):
        self.window = ctk.CTkToplevel(root)
        self.window.title("Take Test")
        self.window.geometry("500x600")

        # Step 1: Select Student
        ctk.CTkLabel(self.window, text="Select Student:").pack(pady=5)
        self.student_dropdown = ctk.CTkOptionMenu(self.window, values=self.get_students())
        self.student_dropdown.pack(pady=5)

        # Step 2: Select Test
        ctk.CTkLabel(self.window, text="Select Test:").pack(pady=5)
        self.test_dropdown = ctk.CTkOptionMenu(self.window, values=self.get_tests())
        self.test_dropdown.pack(pady=5)

        # Step 3: Start Test Button
        self.start_test_btn = ctk.CTkButton(self.window, text="Start Test", command=self.start_test)
        self.start_test_btn.pack(pady=20)

        # Placeholder for Test UI
        self.question_frame = None
        self.submit_btn = None

    def get_students(self):
        """Fetch all students from the database."""
        students = cursor.execute("SELECT id, name FROM students").fetchall()
        return [f"{student[0]} - {student[1]}" for student in students]

    def get_tests(self):
        """Fetch all tests from the database."""
        tests = cursor.execute("SELECT id, title FROM tests").fetchall()
        return [f"{test[0]} - {test[1]}" for test in tests]

    def start_test(self):
        """Start the selected test for the selected student."""
        student_selection = self.student_dropdown.get()
        test_selection = self.test_dropdown.get()

        if not student_selection or not test_selection:
            ctk.messagebox.showerror("Error", "Please select a student and a test!")
            return

        student_id = student_selection.split(" - ")[0]
        test_id = test_selection.split(" - ")[0]

        # Fetch test questions
        test = cursor.execute("SELECT questions FROM tests WHERE id = ?", (test_id,)).fetchone()
        if test:
            self.display_questions(test_id, student_id, test[0])
        else:
            ctk.messagebox.showerror("Error", "Invalid test selection!")

    def display_questions(self, test_id, student_id, questions_json):
        """Display the test questions for the student."""
        import json

        if self.question_frame:
            self.question_frame.destroy()

        self.question_frame = ctk.CTkFrame(self.window)
        self.question_frame.pack(pady=10, fill="both", expand=True)

        questions = json.loads(questions_json)
        self.answers = {}
        self.test_id = test_id
        self.student_id = student_id

        for idx, (question, _) in enumerate(questions.items(), start=1):
            tk_label = ctk.CTkLabel(self.question_frame, text=f"{idx}. {question}")
            tk_label.pack(pady=5)

            answer_entry = ctk.CTkEntry(self.question_frame, placeholder_text="Your Answer")
            answer_entry.pack(pady=5)

            self.answers[question] = answer_entry

        # Submit Button
        if self.submit_btn:
            self.submit_btn.destroy()

        self.submit_btn = ctk.CTkButton(self.window, text="Submit Test", command=self.submit_test)
        self.submit_btn.pack(pady=20)

    def submit_test(self):
        """Submit the test and calculate the score."""
        test_id = self.test_id
        student_id = self.student_id

        # Fetch correct answers from the database
        test = cursor.execute("SELECT questions FROM tests WHERE id = ?", (test_id,)).fetchone()
        if not test:
            ctk.messagebox.showerror("Error", "Test not found!")
            return

        import json
        correct_answers = json.loads(test[0])

        # Calculate score
        score = 0
        total_questions = len(correct_answers)

        for question, correct_answer in correct_answers.items():
            user_answer = self.answers[question].get().strip()
            if user_answer.lower() == correct_answer.lower():
                score += 1

        # Save the result in the database
        cursor.execute("INSERT INTO test_submissions (student_id, test_id, score) VALUES (?, ?, ?)",
                       (student_id, test_id, score))
        conn.commit()

        ctk.messagebox.showinfo("Test Completed", f"You scored {score}/{total_questions}!")
        self.window.destroy()

class ResultsViewerWindow:
    def __init__(self, root):
        self.window = ctk.CTkToplevel(root)
        self.window.title("View Results")
        self.window.geometry("500x500")

        # Step 1: Select Student
        ctk.CTkLabel(self.window, text="Select Student:").pack(pady=5)
        self.student_dropdown = ctk.CTkOptionMenu(self.window, values=self.get_students())
        self.student_dropdown.pack(pady=10)

        # Step 2: View Results Button
        self.view_results_btn = ctk.CTkButton(self.window, text="View Results", command=self.view_results)
        self.view_results_btn.pack(pady=20)

        # Placeholder for Results Display
        self.results_frame = None

    def get_students(self):
        """Fetch all students from the database."""
        students = cursor.execute("SELECT id, name FROM students").fetchall()
        return [f"{student[0]} - {student[1]}" for student in students]

    def view_results(self):
        """Display test results for the selected student."""
        student_selection = self.student_dropdown.get()
        if not student_selection:
            ctk.messagebox.showerror("Error", "Please select a student!")
            return

        student_id = student_selection.split(" - ")[0]

        # Fetch test results for the student
        results = cursor.execute('''
            SELECT t.title, ts.score 
            FROM test_submissions ts
            JOIN tests t ON ts.test_id = t.id
            WHERE ts.student_id = ?
        ''', (student_id,)).fetchall()

        if self.results_frame:
            self.results_frame.destroy()

        self.results_frame = ctk.CTkFrame(self.window)
        self.results_frame.pack(pady=10, fill="both", expand=True)

        if results:
            for idx, (test_title, score) in enumerate(results, start=1):
                result_label = ctk.CTkLabel(self.results_frame, text=f"{idx}. {test_title}: {score} Points")
                result_label.pack(pady=5)
        else:
            ctk.CTkLabel(self.results_frame, text="No results found for this student.").pack(pady=20)






if __name__ == "__main__":
    root = ctk.CTk()
    app = SchoolManagementApp(root)
    root.mainloop()
