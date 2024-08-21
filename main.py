import sqlite3
from datetime import datetime, timedelta

class VaccinationSystem:
    def __init__(self, db_name='vaccination_system.db'):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def create_tables(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS children (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT,
                                    dob TEXT)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    child_id INTEGER,
                                    vaccine TEXT,
                                    appointment_date TEXT,
                                    FOREIGN KEY(child_id) REFERENCES children(id))''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def register_child(self, child_name, dob):
        try:
            self.cursor.execute("INSERT INTO children (name, dob) VALUES (?, ?)", (child_name, dob))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error registering child: {e}")

    def get_child_id(self, child_name):
        try:
            self.cursor.execute("SELECT id FROM children WHERE name = ?", (child_name,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error retrieving child ID: {e}")
            return None

    def schedule_vaccination(self, child_name, vaccine, days_after_birth):
        try:
            child_id = self.get_child_id(child_name)
            if child_id is None:
                return
            self.cursor.execute("SELECT dob FROM children WHERE id = ?", (child_id,))
            dob = datetime.strptime(self.cursor.fetchone()[0], '%Y-%m-%d')
            appointment_date = dob + timedelta(days=days_after_birth)
            self.cursor.execute("INSERT INTO appointments (child_id, vaccine, appointment_date) VALUES (?, ?, ?)",
                                (child_id, vaccine, appointment_date.strftime('%Y-%m-%d')))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error scheduling vaccination: {e}")

    def get_appointments(self, child_name):
        try:
            child_id = self.get_child_id(child_name)
            if child_id is None:
                return []
            self.cursor.execute("SELECT vaccine, appointment_date FROM appointments WHERE child_id = ?", (child_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving appointments: {e}")
            return []

    def send_reminders(self, child_name):
        appointments = self.get_appointments(child_name)
        reminders = []
        today = datetime.today().strftime('%Y-%m-%d')
        for appointment in appointments:
            if today == appointment[1]:
                reminders.append(f"Reminder: {child_name}'s vaccination for {appointment[0]} is today!")
        return reminders

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

# Example Usage
if __name__ == "__main__":
    system = VaccinationSystem()

    # Register a child
    system.register_child('John Doe', '2023-01-01')

    # Schedule vaccinations
    system.schedule_vaccination('John Doe', 'Hepatitis B', 30)  # Schedule for 30 days after birth
    system.schedule_vaccination('John Doe', 'Polio', 60)        # Schedule for 60 days after birth

    # View appointments
    print(system.get_appointments('John Doe'))

    # Send reminders (this would normally run daily)
    print(system.send_reminders('John Doe'))
