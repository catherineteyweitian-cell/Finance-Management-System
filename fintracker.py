#imports necessary modules
#messagesbox = To show popup messages (error/info)
from tkinter import Tk, Label, Entry, Button, Frame, messagebox, simpledialog, Canvas, Text, PhotoImage, Listbox, BOTH, END, LEFT, RIGHT, Toplevel
from tkinter import ttk
import os   # To check if history file exists
from datetime import date, datetime 
import tkinter as tk# For GUI
from calendar import monthrange
import json# For saving and loading tax history as JSON
import uuid
from collections import OrderedDict 
from pathlib import Path

# Always use files from the same folder as fintracker.py
BASE_DIR = Path(__file__).resolve().parent

TAX_HISTORY_FILE = BASE_DIR / "tax_history.json"
USER_FILE = BASE_DIR / "users.txt"
EXPENSE_FILE = BASE_DIR / "user_expenses.txt"
BUDGET_FILE = BASE_DIR / "budget.txt"
SAVINGS_FILE = BASE_DIR / "savings_goals.json"
MUSIC_FILE = BASE_DIR / "just_relax.wav"
LOGIN_IMAGE_FILE = BASE_DIR / "fintracker.png"
BACKGROUND_IMAGE_FILE = BASE_DIR / "bg1.png"

#Exception Handling 1
try:
    import winsound
except ImportError:
    winsound = None # ensure the code doesn't crash

def load_history():
    # Load tax history from JSON file
    if not os.path.exists(TAX_HISTORY_FILE):
        return []
    #Exception Handling 2
    try:
       with open(TAX_HISTORY_FILE, 'r')as f:
           return json.load(f)

    except Exception:
        return []



def save_history(history):
     # Save tax history to JSON file
     with open(TAX_HISTORY_FILE, 'w', encoding='utf-8') as f:
          json.dump(history, f, indent=4, ensure_ascii=False)

class BaseUtility:
    """provid common utility method used by child classes"""
    # Base utility class, providing general methods
    def __init__(self):
        pass

    def convert_to_safe_float(self, value):
        # Safely converts the input value to a float
        """safely convert a value to float,returns 0.0 if conversion fail"""

        if value is None:
            return 0.0

        value = str(value).strip()
        if value == "":
            return 0.0

        return float(value)

class LoginWindow:                                          #User Authentication System (LoginWindow)
    USER_FILE = USER_FILE                                 #file name
    ADMIN_KEY = "ADMINKEY"                                  #registration admin's password

    def __init__(self):
        #login and registration
        if not os.path.exists(LoginWindow.USER_FILE):
            try:
                with open(LoginWindow.USER_FILE, "w") as f: #open file
                    f.write("TAN,1234,admin\n")             #default admin
            except IOError as e:
                                                            # make sure the file detected
                messagebox.showerror("File Creation Error", f"Cannot create user file {LoginWindow.USER_FILE}. Please check permissions. {e}")

        # Use a single root Tk for the application
        self.finwindow = Tk()                               #create the main program window (root)
        self.finwindow.title("FinTracker")                  #window name
        self.finwindow.geometry("1600x900")

        #Exception Handling 3
        # load image safely (don't crash if missing)
        try:
            self.login_bg_image = PhotoImage(file=str(LOGIN_IMAGE_FILE))
            self.login_bg_image_label = Label(self.finwindow, image=self.login_bg_image)
            self.login_bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Cannot load fintracker.png: {e}")
        
        #---Enhanced GUI---
        self.style = ttk.Style()
        self.style.theme_use("clam") # Use a modern theme
        self.style.configure("TButton", padding=6, relief="flat", background="#f0f0f0")
        self.style.map("TButton", background=[('active', '#e0e0e0')])
        self.style.configure("TFrame", background="#B0E0E6") # Top control bar color
        self.style.configure("Treeview.Heading", font=('Times New Roman', 10, 'bold'))

        # Define specific button styles to simulate color effects and fix the TclError
        #red button
        self.style.configure("Red.TButton",font=("Times New Roman",12), background="#E57373", foreground="white")
        self.style.map("Red.TButton", background=[('active', '#D32F2F')])

       #blue button
        self.style.configure("Blue.TButton",font=("Times New Roman",12), background="#4B5CC4", foreground="white")
        self.style.map("Blue.TButton", background=[('active', '#2828FF')])

        #green button
        self.style.configure("Green.TButton",font=("Times New Roman",12), background="#16A951", foreground="white")
        self.style.map("Green.TButton", background=[('active', '#21A675')])

        self.style.configure("Black.TEntry",foreground="black")

        ttk.Button(self.finwindow, text="Sign in", command=self.login_main,width=20, style="Blue.TButton").place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.finwindow.mainloop()

    def login_main(self):
        
        #make the window (Toplevel child of root)
        self.window = Toplevel(self.finwindow)           #create the login dialog as Toplevel
        self.window.title("Expense Tracker Login")       #window name
        self.window.geometry("400x300")                  #window size
        self.window.resizable(False, False)              #set it the window can be resized

        main_frame = Frame(self.window, padx=20, pady=20)# box to hold other things
        main_frame.pack(expand=True, fill="both")        # Make main_frame fill and expand

        Label(main_frame, text="Username:", font=("Times New Roman", 12)).pack(pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30,style="Black.TEntry")
        self.username_entry.pack(pady=5)

        Label(main_frame, text="Password:", font=("Times New Roman", 12)).pack(pady=5)
        self.password_entry = ttk.Entry(main_frame, show="*", width=30,style="Black.TEntry")
        self.password_entry.pack(pady=5)

        # Login button (using ttk, so no bg/fg)
        ttk.Button(main_frame, text="Login", command=self.handle_user_login, width=20,style="Blue.TButton").pack(pady=10)
        # Register button (using ttk, so no bg/fg)
        ttk.Button(main_frame, text="Register", command=self.handle_user_registration, width=20,style="Green.TButton").pack(pady=5)

        # DO NOT call another mainloop here - root already running

    def handle_user_login(self):
        # Handles user login logic
        username = self.username_entry.get().strip()                                              #get the username entered by the user
        password = self.password_entry.get().strip()                                              #get the password entered by the user

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")                  #show error if username or password fields are empty
            return #go back again
        #Exception Handling 4
        try:
            with open(LoginWindow.USER_FILE, "r") as f:
                users = [line.strip().split(",") for line in f if line.strip()]                   #open file and read the username and password
        except FileNotFoundError:
            messagebox.showerror("Error", "User database file not found. Please restart the app.")# if the system cannot open file
            return
        except IOError as e:
            messagebox.showerror("Error", f"Could not read user database file: {e}")              #when user have not register
            return

        for user_data in users:
            if len(user_data) >= 2:
                user, pwd = user_data[0], user_data[1]
                role = user_data[2] if len(user_data) >= 3 else "user"

                if username == user and password == pwd:
                    messagebox.showinfo("Success", f"Welcome, {username}! ")
                    #Exception Handling 5
                    try:
                        self.window.destroy()        #close the login dialog
                        self.finwindow.destroy()        #close the login dialog

                    except Exception:
                        pass
                    # Open the main app window as Toplevel
                    WindowTracker(role, username, master=self.finwindow)
                    return

        messagebox.showerror("Error", "Incorrect username or password.")#when user enter wrong username or password

    def handle_user_registration(self):
        # Handles user registration logic
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        #Exception Handling 6
        try:
            with open(LoginWindow.USER_FILE, "r") as f:
                for line in f:
                    if line.startswith(username + ","):
                        messagebox.showerror("Error", "Username already exists.")
                        return
        except FileNotFoundError:
            # If file doesn't exist yet, it'll be created on write
            pass

        role = "user"
        register_admin = messagebox.askquestion("Role Selection", "Do you want to register as an administrator?")

        if register_admin == "yes":
            admin_key = simpledialog.askstring("Admin Key", "Enter the administrator key:", show="*")
            if admin_key == LoginWindow.ADMIN_KEY:
                role = "admin"
            else:
                messagebox.showerror("Error", "Invalid administrator key. Registering as a standard user.")

        #Exception Handling 7
        try:
            with open(LoginWindow.USER_FILE, "a") as f:
                f.write(f"\n{username},{password},{role}\n")
            messagebox.showinfo("Success", f"Account created successfully! Role: {role}")

            self.finwindow.destroy()
        except IOError as e:
            messagebox.showerror("File Error", f"Cannot write to user file. Permissions may be an issue: {e}")

        #Exception Handling 8
        try:
            # close the login root window if desired (original attempted to); keep root open instead
            if hasattr(self, "window"):
                self.finwindow.destroy()
        except Exception:
            pass
class TaxEstimator:
    """ Progressive tax calculator (parent class) """

    def __init__(self, brackets=None):
        self.brackets = brackets or OrderedDict([
        # Each tuple represents: (income upper limit, tax rate)
            (5000, 0.00), # Income up to 5000 is taxed at 0%
            (20000, 0.05), # Income up to 20000 is taxed at 5%
            (50000, 0.10), # Income up to 50000 is taxed at 10%
            (100000, 0.20), # Income up to 100000 is taxed at 20%
            (float("inf"), 0.30), # Income above 100000 uses a 30% tax rate
        ])

    def calculate_tax(self,income, deduction):# Calculate taxable income by subtracting deductions
        # Progressive tax calculation logic
            # --- flat tax mode: if brackets is float ---
        if isinstance(self.brackets, (float, int)):
            taxable = max(0, income - deduction)
            tax = taxable * self.brackets
            avg_rate = (tax / income) * 100 if income > 0 else 0
            return tax, avg_rate
        
        tax = 0.0
        taxable_income = income-deduction
        
        # Check if income is non-positive
        if taxable_income <= 0:
            return 0.0, 0.0 # Return tax amount and average rate

        previous_limit = 0
        for limit, rate in self.brackets.items():
            if taxable_income > previous_limit:
                # Calculate the amount of income falling into the current bracket
                taxable_in_bracket = min(taxable_income, limit) - previous_limit
                
                # Add tax from this bracket
                tax += taxable_in_bracket * rate
                
                # Update previous limit for the next iteration
                previous_limit = limit

            if taxable_income <= limit:
                break
        
        # Calculate average tax rate
        avg_rate = (tax / income) * 100 if income > 0 else 0.0
        
        return tax, avg_rate

# Tax History management functions (defined outside the class in original, but needed)
        # Uses the global TAX_HISTORY_FILE path
        
    def load_history():
        # Load tax history from JSON file
        if not os.path.exists(TAX_HISTORY_FILE):
            return []
        #Exception Handling 9
        try:
            with open(TAX_HISTORY_FILE, 'r')as f:
                return json.load(f)
        except Exception:
            return []

    def save_history(history):
        # Save tax history to JSON file
        with open(TAX_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    # End of Tax Estimator helper code

    #main application window for expense tracking
    #inheritance: WindowTracker(child) inherits from BaseUtility(father)
class WindowTracker(BaseUtility):
    """The main application window for the Expense Tracker."""
    SAVINGS_FILE = SAVINGS_FILE
    TAX_HISTORY_FILE = TAX_HISTORY_FILE 

    def __init__(self, role, username, master=None):
        super().__init__() #call the BaseUtility 
        self.role = role
        self.current_user = username
        self.expense_file = EXPENSE_FILE #the file to store expense records
        self.tax_calc = TaxEstimator()
        self.history = TaxEstimator.load_history()
        TAX_HISTORY_FILE = "tax_history.json"
        #current month for admin and user filtering
        self.current_month_year = date.today().strftime("%Y-%m")#default current month in 'YYYY-MM' format for filtering expenses
        self.master = master


        #attempt to create expense file
        if not os.path.exists(self.expense_file):
            #Exception Handling 10
            try:
                open(self.expense_file, "w").close()
            except IOError as e:
                messagebox.showerror("File Creation Error", f"Cannot create expense file {self.expense_file}. Please check permissions. {e}")


        self.window = Tk()
        self.window.title(f"FinTracker")
        self.window.geometry("1000x700")

        #music - use same filename as login to be consistent with original intent
        if winsound:
            #Exception Handling 11
            try:
                if MUSIC_FILE.exists():
                    winsound.PlaySound(str(MUSIC_FILE), winsound.SND_ASYNC | winsound.SND_LOOP)
            except:
                pass

        #---Enhanced GUI---
        self.style = ttk.Style()
        self.style.theme_use("clam") # Use a modern theme
        self.style.configure("TButton", padding=6, relief="flat", background="#f0f0f0")
        self.style.map("TButton", background=[('active', '#e0e0e0')])
        self.style.configure("TFrame", background="#B0E0E6") # Top control bar color
        self.style.configure("Treeview.Heading", font=('Times New Roman', 10, 'bold'))

        # Define specific button styles to simulate color effects and fix the TclError
        
        #red button
        self.style.configure("Red.TButton",font=("Times New Roman",12), background="#EA0000", foreground="white")
        self.style.map("Red.TButton", background=[('active', '#FF0000')])

        #pink button
        self.style.configure("Pink.TButton",font=("Times New Roman",12),  background="#E91E63", foreground="white")
        self.style.map("Pink.TButton", background=[('active', '#C2185B')])

        #blue button
        self.style.configure("Blue.TButton",font=("Times New Roman",12),  background="#4B5CC4", foreground="white")
        self.style.map("Blue.TButton", background=[('active', '#2828FF')])

        #light blue button

        #green button
        self.style.configure("Green.TButton",font=("Times New Roman",12),  background="#16A951", foreground="white")
        self.style.map("Green.TButton", background=[('active', '#21A675')])
        
        #Grey button
        self.style.configure("Grey.TButton",font=("Times New Roman",12),  background="#7B7B7B", foreground="white")
        self.style.map("Grey.TButton", background=[('active', '#8E8E8E')])

        #purple button
        self.style.configure("Purple.TButton",font=("Times New Roman",12),  background="#921AFF", foreground="white")
        self.style.map("Purple.TButton", background=[('active', '#B15BFF')])

        #yellow button
        self.style.configure("Yellow.TButton",font=("Times New Roman",12),  background="#FFFF37", foreground="white")
        self.style.map("Yellow.TButton", background=[('active', '#F9F900')])

        #Orange button
        self.style.configure("Orange.TButton",font=("Times New Roman",12),  background="#EA7500", foreground="white")
        self.style.map("Orange.TButton", background=[('active', '#FF8000')])

        #White label and word is red
        self.style.configure("White.TLabel",font=("Times New Roman",12) ,background="white",foreground="red")


        #---UI SETUP---
        #Exception Handling 12
        # Background area label (load safely)
        try:
            self.bg_image = PhotoImage(file=str(BACKGROUND_IMAGE_FILE))  
            self.bg_label = Label(self.window, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Cannot load bg1.png: {e}")

        #top control bar
        self.control_frame = ttk.Frame(self.window, padding="10 10 10 10")
        self.control_frame.pack(side="top", fill="x")

        #---admin mode message---
        if self.role == "admin":
            messagebox.showinfo("Admin Launch", "Admin Mode")
            Label(self.control_frame, text=f"Admin Mode", fg="red", font=("Times New Roman", 12, "bold"), bg="#B0E0E6").pack(side="right", padx=10)

        #core Function Entry Point
        ttk.Button(self.control_frame, text="Exit", command=self.close_window, width=10,style="Red.TButton").pack(side="right", padx=20)
        ttk.Button(self.control_frame, text="Open Personal Finance Assistant Menu", command=self.display_main_menu, width=30,style="Blue.TButton").pack(side="right", padx=20)# go to theexpense tracking menu


        #background and Music buttons
        ttk.Button(self.control_frame, text="Stop Music",command=self.stop_background_music, width=15,style="Red.TButton").pack(side="left", padx=5)
        ttk.Button(self.control_frame, text="Restart Music", command=self.start_background_music, width=15,style="Green.TButton").pack(side="left", padx=5)

        #placed once in the center.
        self.main_content_frame = Frame(self.window, bd=0, relief="flat", bg="#E0E0E0")
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20)) # Fill the main area below the control bar


        #initialize Main Menu Frame (PACKED inside main_content_frame)
        self.expense_frame = Frame(self.main_content_frame, bd=2, relief="groove", padx=15, pady=15, bg="#F0F0F0")
        self.expense_frame.pack_forget()

        #initialize dynamic record frame 
        self.record_expense_frame = Frame(self.main_content_frame, bd=3, relief="raised", padx=10, pady=10, bg="#F9F9F9")
        self.record_expense_frame.pack_forget()

    def close_window(self):
        self.window.destroy()

        
    def play_system_alert_sound(self):
        # Plays a default system alert sound
        """Plays a default system sound using winsound (Windows only)."""
        if winsound:
            #Exception Handling 13
            try:
                winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
            except Exception as e:
                print(f"Winsound error: {e}")

    def stop_background_music(self):
        # Stops the background music
        if winsound:
            #Exception Handling 14
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)#stop music
            except:
                pass


    def start_background_music(self):
        # Restarts playing the background music
        if winsound:
            #Exception Handling 15
            try:
                # use same filename as initial play
                if MUSIC_FILE.exists():
                    winsound.PlaySound(str(MUSIC_FILE), winsound.SND_ASYNC | winsound.SND_LOOP)
                else:
                    messagebox.showwarning("Music Error", "Cannot find 'just_relax.wav' or file format error.")
            except:
                messagebox.showwarning("Music Error", "Cannot play background music.")


    def clear_active_frames(self):
        # Hides all currently active frames to ensure clean page switching
        """Hides all frame to ensure clean page switching."""
        #use pack_forget() for frames to hide
        if hasattr(self, "expense_frame"):
            self.expense_frame.pack_forget()

        if hasattr(self, "record_expense_frame"):
            self.record_expense_frame.pack_forget()

        if hasattr(self, "category_frame"):
            if hasattr(self, "cat_canvas"):
                self.cat_canvas.delete("all")

            self.category_frame.pack_forget() # Changed to pack_forget()

        # Budget Planner frames
        if hasattr(self, "budget_planner_frame"):
            self.budget_planner_frame.pack_forget()

        # Savings Goal Tracker frames
        if hasattr(self, "savings_goal_tracker_frame"):
            self.savings_goal_tracker_frame.pack_forget()

        #destroy temporary query result Frames 
        if hasattr(self, "simple_total_frame") and self.simple_total_frame.winfo_exists():
            self.simple_total_frame.destroy()

        if hasattr(self, "admin_total_frame") and self.admin_total_frame.winfo_exists():
            self.admin_total_frame.destroy()
            
        # Fixed: Destroy tax window if it exists (Toplevel)
        if hasattr(self, "tax_window") and self.tax_window.winfo_exists():
             self.tax_window.destroy()

    #enhanced data loading
    def fetch_filtered_expenses(self, filter_user=None, filter_date=None, filter_month=None):
        # Reads expenses from the file and filters them by user/date/month
        """
        reads expenses from the file and returns a list of records
        records: (username, date, item, amount, category)
        """
        all_expenses = []
        #Exception Handling 16
        try:
            with open(self.expense_file, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 5:
                        record = tuple(parts)
                        username, date, item, amount, category = record

                        is_match = True

                        # 1. user filter (admin views all, user filters by self)
                        actual_filter_user = filter_user if self.role == "admin" else self.current_user
                        if actual_filter_user and username != actual_filter_user:
                            is_match = False

                        # 2. date filter (YYYY-MM-DD)
                        if filter_date and date != filter_date:
                            is_match = False

                        # 3. month filter (YYYY-MM)
                        if filter_month and not date.startswith(filter_month):
                            is_match = False

                        if is_match:
                            all_expenses.append(record)

        except FileNotFoundError:
            #cannot find file
            messagebox.showerror("File Error", f"Data file not found: {self.expense_file}. Please check the path.")

        except IOError as e:
            #permission or other I/O errors
            messagebox.showerror("File Error", f"Cannot read data file {self.expense_file}. Permissions or path may be an issue: {e}")

        except Exception as e:
            #other unexpected errors
            messagebox.showerror("File Error", f"An unexpected error occurred while loading data: {e}")
        return all_expenses

    # ====================== Expense Tracker Core ======================

    def display_main_menu(self):
        # Displays the main menu interface
        """display the main menu frame"""
        self.clear_active_frames()

        #clear and rebuild menu content
        for widget in self.expense_frame.winfo_children():
            widget.destroy()

        Label(self.expense_frame, text="Personal Finance Assistant Menu", font=("Times New Roman", 16, "bold"), bg="#F0F0F0").pack(pady=10)
        
        #menu button
        if self.role == "user":
            ttk.Button(self.expense_frame, text="Expense Tracker", width=40, command=self.display_expense_records,style="Blue.TButton").pack(pady=5)
            ttk.Button(self.expense_frame, text="Budget Planner", width=40,command=self.budget_planner,style="Green.TButton").pack(pady=5)
            ttk.Button(self.expense_frame, text="Savings Goal Tracker", width=40,command=self.savings_goal_tracker,style="Orange.TButton").pack(pady=5)
            ttk.Button(self.expense_frame, text="Simple Tax Estimator", width=40,command=self.simple_tax_estimator,style="Purple.TButton").pack(pady=5) 

        #close menu button
        # Use custom style for color
            ttk.Button(self.expense_frame, text="Close", width=40, command=self.hide_main_menu, style="Red.TButton").pack(pady=15)
        else:
            ttk.Button(self.expense_frame, text="Expense Tracker", width=40, command=self.display_expense_records,style="Blue.TButton").pack(pady=5)
            ttk.Button(self.expense_frame, text="Close", width=40, command=self.hide_main_menu, style="Red.TButton").pack(pady=15)
           

        #pack the menu inside the main_content_frame for stability
        self.expense_frame.pack(expand=True, fill="both", padx=10, pady=10)

    def hide_main_menu(self):
        # Hides the main menu interface
        """hide the main menu frame"""
        self.expense_frame.pack_forget()

    # ---------------------- Record Expense / View All Page ----------------------

    def display_expense_records(self, filter_date=None, filter_month=None, title_suffix=""):
        # Displays the expense record page, including the table view
        """displays the page to view all the expenses"""

        #if entered from the main menu and hide other page
        if filter_date is None and filter_month is None:
            self.clear_active_frames()
            # Pack the frame inside the main_content_frame for stability
            self.record_expense_frame.pack(expand=True, fill="both", padx=10, pady=10)

        #clear and recreate Treeview to ensure correct columns
        for widget in self.record_expense_frame.winfo_children():
            widget.destroy()

        Label(self.record_expense_frame, text=f"Expense Records {title_suffix}", font=("Times New Roman", 14, "bold"), bg="#F9F9F9").pack(pady=5)

        #Treeview setup (includes user column for admin)
        columns = ("Date", "Item", "Amount (RM)", "Category")
        if self.role == "admin":
             columns = ("User", "Date", "Item", "Amount (RM)", "Category") 

        self.tree = ttk.Treeview(self.record_expense_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130 if col != "User" else 70, anchor="center")

        scrollbar = ttk.Scrollbar(self.record_expense_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="top", fill="both", expand=True, pady=10) # Treeview at the top

        #action buttons frame
        button_frame = Frame(self.record_expense_frame, bg="#F9F9F9")
        button_frame.pack(fill="x", pady=10)

        #---total expense button ---
        if self.role != "admin":
            ttk.Button(button_frame, text="Add New Expense", command=self.prompt_and_add_new_expense, width=15,style="Green.TButton").pack(side="left", padx=10)
            ttk.Button(button_frame, text="Show Category Summary", command=self.display_category_chart_page, width=25,style="Blue.TButton").pack(side="left", padx=10)
            ttk.Button(button_frame, text="Filter My Expenses", command=self.prompt_and_display_filtered_expenses, width=18,style="Grey.TButton").pack(side="left", padx=10)
            ttk.Button(button_frame, text="Calculate Daily/Monthly Total", command=self.view_user_daily_monthly_total, width=30,style="Purple.TButton").pack(side="left", padx=10)
        else:
            ttk.Button(button_frame, text="Show Category Summary", command=self.display_category_chart_page, width=25,style="Blue.TButton").pack(side="left", padx=10) 
            ttk.Button(button_frame, text=f"Show Monthly Total ({self.current_month_year})", command=lambda: self.display_admin_monthly_user_totals(self.current_month_year), width=25,style="Green.TButton").pack(side="left", padx=10) #admin monthly total calculation button
            ttk.Button(button_frame, text=f"Change Month", command=self.admin_set_current_month_filter, width=15,style="Grey.TButton").pack(side="left", padx=10) #admin button to change the current month (restores missing functionality

        # Use custom style for color
        ttk.Button(button_frame, text="Close", command=self.hide_expense_records_page, width=15, style="Red.TButton").pack(side="right", padx=10)

        #load data with applied filters
        self.load_expense_data_to_treeview(filter_date=filter_date, filter_month=filter_month)

    def load_expense_data_to_treeview(self, filter_date=None, filter_month=None):
        # Reads expenses from file and loads them into the Treeview table
        """reads expenses from the file and the Treeview, applying filters"""
        if not hasattr(self, "tree"):
            return

        #clear data
        for item in self.tree.get_children():
            self.tree.delete(item)

        #automated data loading
        records = self.fetch_filtered_expenses(
            filter_user=None if self.role == "admin" else self.current_user, # Admin view all
            filter_date=filter_date,
            filter_month=filter_month
        )

        for record in records:
            username, date, item, amount, category = record
            #use def_safe_float
            try:
                amount_val = self.convert_to_safe_float(amount)
            except ValueError:
                amount_val = 0.0
            display_amount = f"RM{amount_val:.2f}"

            if self.role == "admin":
                values = (username, date, item, display_amount, category)
            else:
                values = (date, item, display_amount, category)

            self.tree.insert("", "end", values=values)

    def hide_expense_records_page(self):
        # Hides the expense record page and returns to the menu
        """hide the record frame and display the menu"""
        if hasattr(self, "record_expense_frame"):
            self.record_expense_frame.pack_forget()
        self.display_main_menu()

    def prompt_and_add_new_expense(self):
        # Pops up a dialog to guide the user to add a new expense record
        """open a dialog to add a new expense record"""
        date_str = simpledialog.askstring("Input", "Enter Date (YYYY-MM-DD):", initialvalue=date.today().strftime("%Y-%m-%d")) # Fixed: Used date.today()
        if not date_str:
            messagebox.showwarning("Invalid Input", "Date cannot be empty.")
            return

        if not self.valid_date_ymd(date_str):
            messagebox.showwarning("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
            return


        item = simpledialog.askstring("Input", "Enter Item Name:")
        if not item:
            messagebox.showwarning("Invalid Input", "Item cannot be empty.")
            return

        amount_str = simpledialog.askstring("Input", "Enter Amount (e.g. 50.50):")
        if not amount_str:
            messagebox.showwarning("Invalid Input", "Amount cannot be empty.")
            return

        #use def_safe_float
        try:
            amount_val = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number (e.g. 50.50).")
            return
        if amount_val <= 0:
            messagebox.showerror("Error", "Please enter a valid positive amount.")
            return

        category = simpledialog.askstring("Input", "Enter Category (e.g. Food, Travel):")
        if not category:
            messagebox.showwarning("Invalid Input", "Category cannot be empty.")
            return

        #Exception Handling 17
        #save to file
        try:
            with open(self.expense_file, "a") as f:
                f.write(f"{self.current_user},{date_str},{item},{amount_val:.2f},{category}\n")

            self.play_system_alert_sound()

            messagebox.showinfo("Success", "Expense recorded successfully!")
            self.load_expense_data_to_treeview() # Reload the table
        except IOError as e:
            messagebox.showerror("File Error", f"Cannot save expense record. Permissions or disk space may be an issue: {e}")

    def display_category_summary_text(self):
        # Displays a text summary of expense categories
        """Displays a simple text summary of category totals."""
        totals = {}
        #automated data loading
        records = self.fetch_filtered_expenses(filter_user=None if self.role == "admin" else self.current_user)

        for username, date, item, amount, category in records:
            amt = self.convert_to_safe_float(amount)
            totals[category] = totals.get(category, 0) + amt

        summary = "--- Expense Summary by Category ---\n"
        if not totals:
             summary += "No expense records yet."
        else:
            total_sum = sum(totals.values())
            sorted_totals = sorted(totals.items(), key=lambda item: item[1], reverse=True)
            for cat, amt in sorted_totals:
                percent = (amt / total_sum) * 100 if total_sum > 0 else 0
                summary += f"{cat}: RM{amt:.2f} ({percent:.1f}%)\n"
            summary += f"\nTotal Spending: RM{total_sum:.2f}"

        messagebox.showinfo("Expense Summary", summary)

    def valid_date_ymd(self,date_str):
        if len(date_str) != 10:
            return False
        if date_str[4] != "-" or date_str[7] != "-":
            return False
        y, m, d = date_str.split("-")
        return y.isdigit() and m.isdigit() and d.isdigit()


    def valid_month(self, month_str):
        if len(month_str) != 7:
            return False
        if month_str[4] != "-":
            return False
        y, m = month_str.split("-")
        return y.isdigit() and m.isdigit()

# ---------------------- User Filter View (Implementation) ----------------------
    def prompt_and_display_filtered_expenses(self):
        # Prompts the user for date/month and displays filtered records
        """Prompts user for date/month and displays filtered records."""

        #unified filter entry, let user choose mode
        raw_choice = simpledialog.askstring("Filter Mode", "Enter 'D' to filter by Date (YYYY-MM-DD) or 'M' to filter by Month (YYYY-MM):")

        #KIf user cancels (returns None), exit function
        if raw_choice is None: 
            return #user canceled, return to main menu or current page

        # ensure raw_choice is a string before processing
        choice = raw_choice.strip().upper() 

        filter_date = None
        filter_month = None
        title_suffix = ""

        if choice == "D":
            filter_date = simpledialog.askstring("Filter Date", "Enter Date YYYY-MM-DD (e.g. 2023-10-25):")
            #check if user canceled the second dialog
            if not filter_date:
                 messagebox.showwarning("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
                 return
            if not self.valid_date_ymd(filter_date):
                messagebox.showwarning("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
                return
            title_suffix = f" (Date: {filter_date})"
            
        elif choice == "M":
            filter_month = simpledialog.askstring("Filter Month", "Enter Month YYYY-MM (e.g. 2023-10):")
            #check if user canceled the second dialog
            if not filter_month:
                messagebox.showwarning("Invalid Input", "Please enter a valid month in YYYY-MM format.")
                return

            if not self.valid_month(filter_month):
                messagebox.showwarning("Invalid Input", "Please enter a valid month in YYYY-MM format.")
                return
            title_suffix = f" (Month: {filter_month})"
            
        else:
            messagebox.showwarning("Invalid Input", "Invalid filter mode entered. Please enter 'D' or 'M'.")
            return

        #call show_record_expense_page to display filtered data
        self.display_expense_records(filter_date=filter_date, filter_month=filter_month, title_suffix=title_suffix)
    # ---------------------- Category Page (Bar Chart) ----------------------

    def display_category_chart_page(self):
        # Displays the expense category visualization chart page
        """display the page with the category bar chart"""
        self.clear_active_frames()

        if not hasattr(self, "category_frame") or not self.category_frame.winfo_exists():
            #use main_content_frame as parent
            self.category_frame = Frame(self.main_content_frame, bd=3, relief="raised", padx=10, pady=10, bg="#F9F9F9")

            Label(self.category_frame, text="Category Expense Visualization", font=("Times New Roman", 16, "bold"), bg="#F9F9F9").pack(pady=10) 
            self.cat_canvas = Canvas(self.category_frame, width=750, height=450, bg="white", highlightthickness=1)
            self.cat_canvas.pack(pady=10, padx=10)

            ttk.Button(self.category_frame, text="Show Category Summary (Text)", command=self.display_category_summary_text, width=25,style="Blue.TButton").pack(side="left", padx=10) 
            ttk.Button(self.category_frame, text="Close", command=self.display_expense_records, width=20, style="Red.TButton").pack(side="right",pady=10)

        #pack the frame inside the main_content_frame for stability
        self.category_frame.pack(expand=True, fill="both", padx=10, pady=10)
        self.draw_category_bar_chart()


    def hide_category_chart_page(self):
        # Hides the category chart page and returns to the menu
        """hide the category chart frame and display the menu"""
        if hasattr(self, "category_frame"):
            self.category_frame.pack_forget()
        self.display_main_menu()

    def draw_category_bar_chart(self):
        # Calculates category totals and draws a bar chart on the Canvas
        """calculate category total and draws a bar chart on the Canvas"""
        if not hasattr(self, "cat_canvas"):
            return

        self.cat_canvas.delete("all")
        totals = {}

        #automated data loading
        records = self.fetch_filtered_expenses(filter_user=None if self.role == "admin" else self.current_user)

        for username, date, item, amount, category in records:
            amt = self.convert_to_safe_float(amount)
            totals[category] = totals.get(category, 0) + amt

        if not totals:
            self.cat_canvas.create_text(375, 225, text="No expense records available for charting.", font=("Times New Roman", 14))
            return

        #drawing logic
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#E91E63", "#9C27B0"]                # list of bar colors
        canvas_width, canvas_height = 500, 450                                          # canvas size
        max_amount = max(totals.values())                                               # max value in totals
        x_axis_margin, y_axis_margin = 150, 30                                          # left and top margins
        bar_height, gap = 30, 20                                                        # height of each bar and gap between bars
        max_bar_width = canvas_width - x_axis_margin - 50                               # max width of a bar
        sorted_totals = sorted(totals.items(), key=lambda item: item[1], reverse=True)  # sort totals descending
        total_sum = sum(totals.values())                                                # sum of all totals
        current_y = y_axis_margin                                                       # starting y position for drawing bars

        for i, (cat, amt) in enumerate(sorted_totals):
            if current_y + bar_height > canvas_height - y_axis_margin:
                break 

            length = (max(0, amt) / max_amount) * max_bar_width
            color = colors[i % len(colors)]
            percent = (amt / total_sum) * 100 if total_sum > 0 else 0

            #draw bar and label
            self.cat_canvas.create_rectangle(x_axis_margin, current_y, x_axis_margin + length, current_y + bar_height, fill=color, outline="")
            self.cat_canvas.create_text(x_axis_margin - 10, current_y + bar_height/2, text=cat, anchor="e", font=("Times New Roman", 10, "bold"))

            label_text = f"RM{amt:.2f} ({percent:.1f}%)"
            text_x = x_axis_margin + length + 5
            self.cat_canvas.create_text(text_x, current_y + bar_height/2, text=label_text, anchor="w", font=("Times New Roman", 10))

            current_y += bar_height + gap

        #draw baseline (y-axis)
        self.cat_canvas.create_line(x_axis_margin, y_axis_margin, x_axis_margin, current_y - gap, width=2, fill="gray")


    # ---------------------- Simple View Methods (Modified) ----------------------

    def view_user_daily_monthly_total(self):
        #calculate and display the user's daily or monthly total expenses
        #user simple view for daily or monthly total spending

        raw_choice = simpledialog.askstring("Mode", "Enter 'D' for Daily, 'M' for Monthly:")
        if raw_choice is None:
            return
        choice = raw_choice.strip().upper()
        if choice not in ("D","M"):
            messagebox.showwarning("Invalid Input", "Please enter 'D' for Daily or 'M' for Monthly.")
            return 

        total = 0.0
        text = ""

        #load data using unified method
        lines = self.fetch_filtered_expenses(filter_user=self.current_user)

        if choice=="D":
            date_str = simpledialog.askstring("Daily Total", "Enter Date YYYY-MM-DD (e.g. 2025-10-25):")
            if not date_str:
                messagebox.showwarning("Invalid Input", "Invalid.")
                return
            if not self.valid_date_ymd(date_str):
                messagebox.showwarning("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
                return

            for u,d,item,amt,cat in lines:
                if d==date_str:
                    total += self.convert_to_safe_float(amt)
            text = f"Total spending for {date_str}: RM{total:.2f}"

        else: #when choice == "M"
            month_str = simpledialog.askstring("Monthly Total", "Enter Month YYYY-MM (e.g. 2025-10):")
            if not month_str:
                messagebox.showwarning("Invalid Input", "Invalid.")
                return
            
            if not self.valid_month(month_str):
                messagebox.showwarning("Invalid Input", "Please enter a valid month in YYYY-MM format.")
                return


            for u,d,item,amt,cat in lines:
                if d.startswith(month_str):
                    total += self.convert_to_safe_float(amt)
            text = f"Total spending for {month_str}: RM{total:.2f}"


        #destroy existing frame if it exists before creating a new one
        if hasattr(self, "simple_total_frame") and self.simple_total_frame.winfo_exists(): self.simple_total_frame.destroy()

        #temporary frame to display results, includes close button
        self.simple_total_frame = Frame(self.window, bd=3, relief="raised", padx=20, pady=20, bg="#F0F0F0")
        self.simple_total_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=200)

        Label(self.simple_total_frame, text="Total Spending Query Result", font=("Times New Roman", 14, "bold"), bg="#F0F0F0").pack(pady=10)
        Label(self.simple_total_frame, text=text, font=("Times New Roman", 12), bg="#F0F0F0", fg="blue").pack(pady=5)
        # Use custom style for color
        ttk.Button(self.simple_total_frame, text="Close", command=self.simple_total_frame.destroy, width=10, style="Red.TButton").pack(pady=5)

    #admin can switch months
    def admin_set_current_month_filter(self):
        # Admin view: Allows changing the month filter
        # Admin view: Allows changing the month.

        #allow admin to input month
        month_str = simpledialog.askstring("Month Filter", f"Enter Month YYYY-MM (Current: {self.current_month_year}):")
        if not month_str:
            messagebox.showwarning("Invalid Input", "Invalid.")
            return # Cancelled

        if not self.valid_month(month_str):
            messagebox.showwarning("Invalid Input", "Please enter a valid month in YYYY-MM format.")
            return
        
        #Exception Handling 18
        try:
            #simple YYYY-MM format
            datetime.strptime(month_str, '%Y-%m')
            self.current_month_year = month_str
        except ValueError:
            # Exception Handling
            messagebox.showerror("Error", "Invalid month format. Please use YYYY-MM.")
            return

        messagebox.showinfo("Success", f"Admin's current expense month set to: {self.current_month_year}. Click 'Show Monthly Total' to view data.")

        self.display_expense_records()


    def display_admin_monthly_user_totals(self, month_str):
        # Calculates and displays the total expenses of all users for the month selected by the administrator
        #internal function to calculate and display the admin monthly total

        #ensure user and admin use the current month 
        if not month_str:
             month_str = self.current_month_year

        #destroy existing frame if it exists before creating a new one
        if hasattr(self, "admin_total_frame") and self.admin_total_frame.winfo_exists(): self.admin_total_frame.destroy()

        totals = {}
        # automated data loading
        records = self.fetch_filtered_expenses(filter_month=month_str)

        for u,d,item,amt,cat in records:
            totals[u] = totals.get(u,0)+self.convert_to_safe_float(amt)

        #temporary frame and text component to display results, includes close button
        self.admin_total_frame = Frame(self.window, bd=3, relief="raised", padx=10, pady=10, bg="#F9F9F9")
        self.admin_total_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=350)

        Label(self.admin_total_frame, text=f"--- {month_str} Monthly Total per User ---", font=("Times New Roman", 14, "bold"), bg="#F9F9F9").pack(pady=10)

        admin_total_text = Text(self.admin_total_frame, width=40, height=10, bg="#FFF3E0")
        admin_total_text.pack(pady=5)

        if not totals:
            admin_total_text.insert("end","No records found for this month.\n")
        else:
            for u,amt in sorted(totals.items(), key=lambda item: item[1], reverse=True):
                admin_total_text.insert("end", f"{u}: RM{amt:.2f}\n")

        admin_total_text.config(state="disabled")
        # Use custom style for color
        ttk.Button(self.admin_total_frame, text="Close", command=self.admin_total_frame.destroy, width=10, style="Red.TButton").pack(pady=10)

    def budget_planner(self):
        """Open the budget planner page."""  # Function docstring: opens the budget planner UI
        self.clear_active_frames()  # Hide other frames before showing this one
        if not hasattr(self, "budget_planner_frame"):  # If the frame isn't created yet
            # Set a modern, clearer UI color
            self.budget_planner_frame = Frame(self.main_content_frame, bd=3, relief="raised", padx=10, pady=10, bg="#F0F8FF")  # Create the main frame with padding and background color

        self.budget_file = BUDGET_FILE  # File name to save/load budgets
        if not hasattr(self, 'budget_data'):
            self.budget_data = []  # Initialize in-memory list for budget data

        # Pack the main budget frame to make it visible
        self.budget_planner_frame.pack(expand=True, fill="both", padx=10, pady=10)  # Show the frame in the UI

        # --- UI Rework: All Inputs Visible & New Layout ---
        # Clear previous content
        for widget in self.budget_planner_frame.winfo_children():
            widget.destroy()  # Remove any existing widgets in the frame

        # Title
        Label(self.budget_planner_frame, text="Budget Planner", font=("Times New Roman", 16, "bold"), bg="#F0F8FF").pack(pady=10)  # Add title label

        # Main Area Frame (Input Panel on left, Control/Display Panel on right)
        main_area = Frame(self.budget_planner_frame, bg="#F0F8FF")  # Container for left and right panels
        main_area.pack(fill="both", expand=True)  # Let it expand to fill available space

        # 1. Input Panel (Left) - Contains all income/budget entries
        self.budget_input_panel = Frame(main_area, padx=15, pady=15, bg="#E6E6FA", bd=2, relief="groove")  # Create the input panel
        self.budget_input_panel.pack(side="left", fill="y", padx=10, pady=10)  # Place input panel on left

        # Dictionary to hold Entry widgets for easy access when saving
        self.budget_entries = {}  # Will map field names to Entry widgets

        # Build input UI
        self.budget_input_ui()  # Call helper to add input fields

        # 2. Control & Display Panel (Right) - Contains buttons and list/variance view
        self.budget_control_display_panel = Frame(main_area, padx=5, pady=5, bg="#F0F8FF")  # Right panel container
        self.budget_control_display_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)  # Place it to the right

        # Add core control buttons to the right panel
        self.create_budget_controls()  # Add buttons like Save, Load, Clear

        # Display area for list/variance
        self.display_page_frame = Frame(self.budget_control_display_panel, bg="#FFFFFF", bd=1, relief="sunken")  # Area to show list or variance
        self.display_page_frame.pack(fill="both", expand=True, pady=10)  # Let it expand

        self.page_frame = self.display_page_frame  # Keep a reference for building pages

        # Initial view: show the budget list
        self.open_list()  # Show the list view when opening planner


    # ==========change FRAME system ==========
    def show_budget_planner_frame(self, builder):
        """Hides previous content in page_frame and calls the builder function."""  # Doc: helper to rebuild page content
        if hasattr(self, "page_frame"):
            for widget in self.page_frame.winfo_children():
                widget.destroy()  # Clear current page widgets
        builder()  # Run the builder to create new page content


    # ---------- MAIN MENU (controls for right panel) ----------
    def create_budget_controls(self):
        """Builds the control buttons and the display frame for the budget planner (Load/Save/List/Variance)."""  # Doc

        # Clear display panel content before adding new controls
        for widget in self.budget_control_display_panel.winfo_children():
            widget.destroy()  # Remove old widgets from control panel

        # Add buttons to the top of the control/display panel
        control_frame = Frame(self.budget_control_display_panel, bg="#F0F8FF")  # Small frame for buttons
        control_frame.pack(fill="x", pady=10)  # Pack it horizontally

        ttk.Button(control_frame, text="Clear All", command=self.clear_budget_data, width=15, style="Red.TButton").pack(side=LEFT, padx=5)  # Clear button
        ttk.Button(control_frame, text="Load Data", command=self.load_budget_data_from_file_and_refresh, width=15, style="Blue.TButton").pack(side=LEFT, padx=5)  # Load button
        ttk.Button(control_frame, text="Show Budget List", command=self.open_list, width=18, style="Orange.TButton").pack(side=LEFT, padx=5)  # Show list
        ttk.Button(control_frame, text="Show Variance", command=self.open_variance, width=18, style="Purple.TButton").pack(side=LEFT, padx=5)  # Show variance
        ttk.Button(control_frame, text="Close", command=self.hide_budget_planner_frame, width=15, style="Red.TButton").pack(side=RIGHT, padx=5)  # Close planner

        # The display_page_frame is created in budget_planner(); keep it as is.


    def hide_budget_planner_frame(self):
        """hide the record frame and display the menu"""  # Doc: hide planner and go back to main menu
        if hasattr(self, "budget_planner_frame"):
            self.budget_planner_frame.pack_forget()  # Hide the planner frame
        self.display_main_menu()  # Show main menu


    # ---------- ADD BUDGET (kept for compatibility but not used by consolidated UI) ----------
    def add_budget(self, budget_type, entry_widget, frame):
        """add a single budget item"""  # Doc: older method to add one item

        value = entry_widget.get()  # Read value from the entry widget
        if not value.strip():
            messagebox.showerror("Invalid", "Input cannot be empty!")  # Show error if empty
            return
        
        #Exception Handling 19
        try:
            amount = float(value)  # Convert to float
            formatted = f"{amount:.2f}"  # Format to 2 decimals
            # Keep old text-based format for compatibility: "Type : RMxx.xx"
            self.budget_data.append(f"{budget_type} : RM{formatted}")  # Add to in-memory list
            messagebox.showinfo("Success", f"{budget_type} set to RM{formatted}")  # Inform user

            # After adding, refresh consolidated entries if present
            self.load_budgets_to_entries()  # Update input fields from data
            self.open_list()  # Show list view
        except ValueError:
            messagebox.showerror("Invalid", "Enter numbers only (eg: 10, 10.50)")  # Invalid number
            return


    # --- CONSOLIDATED INPUT UI ---
    def budget_input_ui(self):
        """Builds a single, consolidated UI for Income and all Budget categories. Inputs placed outside old page_frame."""  # Doc
        """Create all input fields for income and budgets."""  # Doc repeated

        Label(self.budget_input_panel, text="Set Monthly Income & Budgets", font=("Times New Roman", 12, "bold"), bg="#E6E6FA").pack(pady=5)  # Section header

        # --- 1. Income Input ---
        income_frame = Frame(self.budget_input_panel, bg="#E6E6FA")  # Frame for income row
        income_frame.pack(fill="x", pady=5)  # Pack horizontally
        Label(income_frame, text="Income (RM):", font=("Times New Roman", 12), bg="#E6E6FA").pack(side=LEFT, padx=5)  # Label
        income_entry = Entry(income_frame, font=("Times New Roman", 12), width=12)  # Entry for income
        income_entry.pack(side=RIGHT, padx=5)  # Pack entry to the right
        self.budget_entries["Income"] = income_entry  # Save reference

        ttk.Separator(self.budget_input_panel, orient='horizontal').pack(fill='x', pady=8)  # Visual separator

        # --- 2. Category Inputs ---
        categories = ["Food Budget", "Transportation Budget", "Entertainment Budget",
                      "Beverage Budget", "Stationery Budget", "Other Budget"]  # List of categories

        for cat in categories:
            cat_frame = Frame(self.budget_input_panel, bg="#E6E6FA")  # Row frame for category
            cat_frame.pack(fill="x", pady=4)  # Pack row
            display_cat = cat.replace(" Budget", "")  # Short label without 'Budget'
            Label(cat_frame, text=f"{display_cat} (RM):", font=("Times New Roman", 12), bg="#E6E6FA").pack(side=LEFT, padx=5)  # Label

            cat_entry = Entry(cat_frame, font=("Times New Roman", 12), width=12)  # Entry field
            cat_entry.pack(side=RIGHT, padx=5)  # Pack entry
            self.budget_entries[cat] = cat_entry  # Store reference

        # --- 3. Action Button ---
        ttk.Button(self.budget_input_panel, text="Save All Budgets", command=self.save_consolidated_budgets, width=16, style="Green.TButton").pack(pady=12)  # Save button

        # Load existing data into entries
        self.load_budgets_to_entries()  # Fill entries with any saved values

    def clear_budget_data(self):
        """Clear all loaded budget data and refresh the UI."""  # Doc
        """Clear all budget data."""
    
        # Clear stored budget data
        self.budget_data.clear()  # Empty the list

        # Reset all input entries
        if hasattr(self, 'budget_entries'):
            for entry in self.budget_entries.values():
                entry.delete(0, END)  # Remove current text
                entry.insert(0, "0.00")  # default display 0.00

        # clear the budget listbox (only if it still exists)
        if hasattr(self, 'budget_list') and self.budget_list.winfo_exists():
            self.budget_list.delete(0, END)  # Clear listbox items
    
        # Reset total budget display
        if hasattr(self, 'total_label'):
            self.total_label.config(text="Total Budget: RM0.00")  # Reset label


    # ---------- LIST PAGE ----------
    def open_list(self):
        # Build list view on the right display area
        """Show the budget list page."""  # Doc
        def build():
            Label(self.page_frame, text="Budget List", font=("Times New Roman", 14, "bold")).pack(pady=10)  # Header label

            # Frame to contain Listbox and Scrollbar
            list_frame = Frame(self.page_frame)  # Container for list and scrollbar
            list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))  # Pack with padding

            self.budget_list = Listbox(list_frame, width=50, height=15, font=("Times New Roman", 12))  # Create listbox
            self.budget_list.pack(side="left", fill="both", expand=True)  # Pack listbox

            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.budget_list.yview)  # Scrollbar linked to listbox
            scrollbar.pack(side="right", fill="y")  # Pack scrollbar
            self.budget_list.config(yscrollcommand=scrollbar.set)  # Connect scrollbar

            # Populate the listbox
            self.budget_list.delete(0, END)  # Clear any existing entries
            for item in self.budget_data:
                self.budget_list.insert(END, item)  # Insert each budget line

            self.total_label = Label(self.page_frame, text="", font=("Times New Roman", 12, "bold"))  # Label for total
            self.total_label.pack(pady=5)  # Pack total label
            self.update_total_label()  # Update total text

        self.show_budget_planner_frame(build)  # Show this built page


    def update_total_label(self):
        """calculates and updates the total budget label"""  # Doc
        """Update the total budget label."""

        total_budget = self.calculate_total_budget()  # Compute total
        if hasattr(self, 'total_label') and self.total_label.winfo_exists():
            self.total_label.config(text=f"Total Budget: RM{total_budget:.2f}", fg="black")  # Update label text


    def calculate_total_budget(self):
        """
        Calculate total budget from self.budget_data.

        Supports both legacy "Type : RMxx.xx" and safe parsed "Type,xx.xx" lines
        but will prefer extracting numeric value robustly.
        """  # Doc explaining parsing
        """Calculate total budget (excluding income)."""

        total = 0.0  # Start with zero
        for item in self.budget_data:
            #Exception Handling 20
            try:
                line = item.strip()  # Trim whitespace
                if "RM" in line:
                    # Legacy format: "Food Budget : RM120.00" or "Income : RM1200.00"
                    parts = line.split("RM")  # Split at RM
                    amount = float(parts[-1].strip())  # Parse last part as float
                    # For budget total we exclude Income
                    if "Income" not in line:
                        total += amount  # Add amount if not income
                elif "," in line:
                    # Newer safe fallback format: "Food Budget,120.00" or "Income,1200.00"
                    name, amt = line.split(",", 1)  # Split into name and amount
                    amt_val = float(amt.strip())  # Parse amount
                    if "Income" not in name:
                        total += amt_val  # Add if not income
            except Exception:
                # ignore any malformed lines
                continue  # Skip bad lines
        return total  # Return computed total


    # ---------- SAVE & LOAD ----------
    def save_budget_to_file(self):
        """Save budget data to file."""  # Doc
        if not self.budget_data:
            messagebox.showwarning("No Data", "No budget data to save!")  # Warn if nothing to save
            return
        
        #Exception Handling 21
        try:
            with open(self.budget_file, "w", encoding="utf-8") as file:  # Open file for writing
                for item in self.budget_data:
                    file.write(item + "\n")  # Write each line
            messagebox.showinfo("Saved", "Budget data saved!")  # Inform user
        except Exception as e:
            messagebox.showerror("Error", f"Could not save budget data: {e}")  # Show error


    def load_budget_from_file(self):
        """Load budget data from file."""  # Doc
        #Exception Handling 22
        try:
            with open(self.budget_file, "r", encoding="utf-8") as file:  # Open file to read
                self.budget_data.clear()  # Clear current data
                if hasattr(self, 'budget_list'):
                    #Exception Handling 23
                    try:
                        self.budget_list.delete(0, END)  # Clear listbox if exists
                    except Exception:
                        pass  # Ignore deletion errors

                    for line in file:
                        cleaned = line.strip()  # Trim newline
                        if cleaned:
                            # Be tolerant: preserve file line as-is (old format) but also accept "Type,amount"
                            self.budget_data.append(cleaned)  # Add to list
                            if hasattr(self, 'budget_list'):
                                self.budget_list.insert(END, cleaned)  # Insert into listbox
                else:
                    # If budget_list doesn't exist yet, still read into budget_data
                    for line in file:
                        cleaned = line.strip()
                        if cleaned:
                            self.budget_data.append(cleaned)  # Add to data

            self.update_total_label()  # Update total after loading
            messagebox.showinfo("Loaded", "Data loaded successfully!")  # Inform user
        except FileNotFoundError:
            messagebox.showerror("Error", "No file found. Save first!")  # File not found
        except Exception as e:
            messagebox.showerror("Error", f"Could not load budget data: {e}")  # Other errors


    def save_consolidated_budgets(self):
        """Save all entries from the consolidated UI into budget_data and to file using legacy readable format."""  # Doc
        """Save all input fields into budget_data."""

        self.budget_data.clear()  # Clear existing in-memory data before saving new set

        all_saved = True  # Flag to track if all inputs saved

        for budget_type, entry_widget in self.budget_entries.items():
            value = entry_widget.get().strip()  # Read value text

            #Exception Handling 24
            try:
                if not value:
                    # If empty, treat as zero for Income, skip for other budgets
                    if budget_type == "Income":
                        amount = 0.00  # Default income to 0
                    else:
                        continue  # Skip empty category
                else:
                    amount = float(value)  # Parse value

                formatted = f"{amount:.2f}"  # Format to 2 decimals
                # Use human-readable legacy format: "Type : RMxx.xx"
                self.budget_data.append(f"{budget_type} : RM{formatted}")  # Append line
                # update entry display to formatted value
                entry_widget.delete(0, END)  # Clear entry
                entry_widget.insert(0, formatted)  # Insert formatted text
            except ValueError:
                messagebox.showerror("Invalid", f"Invalid amount entered for {budget_type}. Please use numbers only.")  # Error for bad input
                all_saved = False  # Mark failure

        if all_saved:
            self.save_budget_to_file()  # Save to disk
            self.update_total_label()  # Update totals
            self.open_list()  # Show list
            messagebox.showinfo("Saved", "Budget data saved!")  # Inform user


    def load_budgets_to_entries(self):
        """Loads budget data from self.budget_data and updates the entry widgets."""  # Doc
        """Load budget_data values into the entry fields."""

        if not hasattr(self, 'budget_entries'):
            return  # Nothing to fill

        # Build a mapping from budget_type -> amount string
        data_map = {}  # Map to hold parsed values
        for item in self.budget_data:
            line = item.strip()  # Trim whitespace
            # support "Type : RMxx.xx"
            if "RM" in line:
                try:
                    left, right = line.split("RM", 1)  # Split into left and right
                    budget_type = left.replace(":", "").strip()  # Clean budget type name
                    amount_str = right.strip()  # Amount text
                    data_map[budget_type] = amount_str  # Store in map
                except Exception:
                    continue  # Skip malformed
            elif "," in line:
                # support fallback "Type,amount"
                #Exception Handling 25
                try:
                    budget_type, amount_str = line.split(",", 1)  # Split into two parts
                    data_map[budget_type.strip()] = amount_str.strip()  # Store clean values
                except Exception:
                    continue  # Skip bad lines

        # Populate entries; keep human-friendly default "0.00"
        for budget_type, entry_widget in self.budget_entries.items():
            entry_widget.delete(0, END)  # Clear entry
            amount_str = data_map.get(budget_type, data_map.get(budget_type.replace(" Budget", ""), "0.00"))  # Lookup amount
            entry_widget.insert(0, amount_str)  # Insert found or default


    def load_budget_data_from_file_and_refresh(self):
        """Loads data from file and then refreshes the input entries and the list view."""  # Doc
        """Load data from file and refresh UI."""
        self.load_budget_from_file()  # Read file into memory
        self.load_budgets_to_entries()  # Update input fields
        if hasattr(self, 'budget_list'):
            self.open_list()  # Refresh list view if exists


    # ---------- VARIANCE ----------
    def open_variance(self):
        """Show variance between income and total budget."""  # Doc
        def build():
            # Collect income from budget_data robustly (supporting both formats)
            income_total = 0.0  # Start income at zero
            for item in self.budget_data:
                #Exception Handling 26
                try:
                    line = item.strip()  # Trim
                    if "Income" in line:
                        if "RM" in line:
                            income_total += float(line.split("RM")[1].strip())  # Parse income from RM format
                        elif "," in line:
                            income_total += float(line.split(",", 1)[1].strip())  # Parse income from CSV format
                except Exception:
                    continue  # Skip bad lines

            total_budget = self.calculate_total_budget()  # Compute total budget
            variance = income_total - total_budget  # Income minus expense

            Label(self.page_frame, text=f"Total Income: RM{income_total:.2f}", font=("Times New Roman", 16)).pack(pady=10)  # Show income
            Label(self.page_frame, text=f"Total Budget: RM{total_budget:.2f}", font=("Times New Roman", 16)).pack(pady=10)  # Show budget

            result_label = Label(self.page_frame, text=f"Variance: RM{variance:.2f}", font=("Times New Roman", 18, "bold"))  # Label for variance
            result_label.config(fg="green" if variance >= 0 else "red")  # Green if surplus, red if deficit
            result_label.pack(pady=10)  # Pack label

            ttk.Button(self.page_frame, text="OK", command=self.open_list, width=20, style="Blue.TButton").pack(pady=10)  # OK button

        self.show_budget_planner_frame(build)  # Show the variance page


    def savings_goal_tracker(self):
        # Font Same By Times New Roman
        self.font_main = ("Times New Roman",12)
        self.font_title = ("Times New Roman",14,"bold")
        self.font_small = ("Times New Roman",11)

        # ------------------- Logic for embedding the frame -------------------
        self.clear_active_frames()
        self.goals = self.load_goals()# Load Data

        if not hasattr(self, "savings_goal_tracker_frame") or not self.savings_goal_tracker_frame.winfo_exists():
             # Outer frame within main_content_frame
             self.savings_goal_tracker_frame = Frame(self.main_content_frame, bd=3, relief="raised", padx=10, pady=10, bg="#F9F9F9")

        # Create the dynamic page frame
        if not hasattr(self, "savings_goal_trackerpage_frame") or not self.savings_goal_trackerpage_frame.winfo_exists():
            self.savings_goal_trackerpage_frame = Frame(self.savings_goal_tracker_frame, bg="#F0F0F0")
            self.savings_goal_trackerpage_frame.pack(fill="both", expand=True)
                # ------------------- End of frame embedding logic -------------------

            # Leftside Listbox + Scrollbar
            self.listbox_frame = tk.Frame(self.savings_goal_trackerpage_frame)
            self.listbox_frame.pack(side="left", fill="y")

            self.listbox = tk.Listbox(self.listbox_frame, width=40, height=20, font=self.font_main)
            self.listbox.pack(side="left", fill="y")
            self.listbox.bind("<<ListboxSelect>>", self.show_goal_detail)

            self.scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview)
            self.scrollbar.pack(side="left", fill="y")
            self.listbox.config(yscrollcommand=self.scrollbar.set)

            # Rightside Detail Frame
            self.detail_frame = tk.Frame(self.savings_goal_trackerpage_frame)
            self.detail_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

            self.detail_label = tk.Label(self.detail_frame, text="Select a goal", justify="left", font=self.font_main)
            self.detail_label.pack()

            # Button Frame (placed at the bottom of the *main* outer frame)
            btn_frame = tk.Frame(self.savings_goal_tracker_frame)
            btn_frame.pack(side="bottom", pady=10)

            ttk.Button(btn_frame, text="Add Goal", command=self.add_goal,width=15,style="Green.TButton").pack(side="left",padx=10)
            ttk.Button(btn_frame, text="Add Saving", command=self.add_saving_to_goal,width=15,style="Blue.TButton").pack(side="left",padx=10)
            ttk.Button(btn_frame, text="Delete Goal", command=self.delete_selected_goal,width=15,style="Pink.TButton").pack(side="left",padx=10)
            ttk.Button(btn_frame, text="Close", command=self.hide_savings_goal_tracker_frame,width=15,style="Red.TButton").pack(side="right",padx=10)

        if hasattr(self, "detail_frame") and self.detail_frame.winfo_exists():
            for widget in self.detail_frame.winfo_children():
                widget.destroy()
                
            self.detail_label = tk.Label(self.detail_frame, text="Select a goal", justify="left", font=self.font_main)
            self.detail_label.pack()
            
        self.savings_goal_tracker_frame.pack(expand=True, fill="both", padx=10, pady=10)

        if hasattr(self, "listbox") and self.listbox.winfo_exists():
            self.refresh_listbox()

    def hide_savings_goal_tracker_frame(self):
        """Hides the savings goal tracker frame and returns to the main menu."""
        if hasattr(self, "savings_goal_tracker_frame"):
            self.savings_goal_tracker_frame.pack_forget()
        self.display_main_menu()
        

    # The builder function is not needed in this layout, but if you keep it:
    def show_savings_goal_tracker_frame(self, builder):
        """Hides previous content in page_frame and calls the builder function."""
        if hasattr(self, "savings_goal_trackerpage_frame"): 
            for widget in self.savings_goal_trackerpage_frame.winfo_children():
                widget.destroy()

        # Build the new page content
        builder()

    # Reload Listbox
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for g in self.goals:
            progress = (g['current_amount'] / g['target_amount'])*100 if g['target_amount'] else 0
            display = f"{g['title']} (RM{g['current_amount']:.2f}/{g['target_amount']:.2f}) {progress:.0f}%"
            self.listbox.insert(tk.END, display)

    # Show Goal Detail
    def show_goal_detail(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        g = self.goals[index]

        # Delete Detail Frame
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # Title
        tk.Label(self.detail_frame, text=g['title'], font=self.font_title).pack(anchor="w", pady=5)

        # Progress Bar（Limit Percentage Display 100%，But Amount Is Real）
        progress_percentage = min((g['current_amount'] / g['target_amount'])*100 if g['target_amount'] else 0, 100)
        progress_bar = ttk.Progressbar(self.detail_frame, length=300, value=progress_percentage)
        progress_bar.pack(pady=5)

        # Current Amount / Target Amount + Percentage（Actual Amount Display）
        progress_real = (g['current_amount'] / g['target_amount'])*100 if g['target_amount'] else 0
        text_color = "orangered" if progress_real > 100 else "black"
        tk.Label(self.detail_frame, text=f"Saved: RM{g['current_amount']:.2f} / RM{g['target_amount']:.2f} ({progress_real:.0f}%)",font=self.font_small, fg=text_color).pack(anchor="w", pady=2)

        # Create Time / Target Date
        tk.Label(self.detail_frame, text=f"Created: {g['created_at']}\nTarget Date: {g['target_date']}",font=self.font_small, justify="left").pack(anchor="w", pady=2)

        # History Grouping
        history_frame = tk.LabelFrame(self.detail_frame, text="History", font=self.font_title)
        history_frame.pack(fill="both", pady=5)

        # Make History Become Scroll
        history_canvas = tk.Canvas(history_frame)
        history_scroll = tk.Scrollbar(history_frame, orient="vertical", command=history_canvas.yview)
        history_inner = tk.Frame(history_canvas)

        history_inner.bind("<Configure>", lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all")))
        history_canvas.create_window((0,0), window=history_inner, anchor="nw")
        history_canvas.configure(yscrollcommand=history_scroll.set)
        history_canvas.pack(side="left", fill="both", expand=True)
        history_scroll.pack(side="right", fill="y")

        for h in g["history"]:
            note_text = f" ({h['note'].strip()})" if 'note' in h and h['note'].strip() else "" 
            tk.Label(history_inner, text=f"{h['date']}: RM{h['amount']:.2f}{note_text}",
                     font=self.font_small, anchor="w").pack(fill="x")

    # Add New Goal
    def add_goal(self):
        title = simpledialog.askstring("New Goal", "Goal Title:")
        if not title:
            return
        #Exception Handling 27
        try:
            target_amount = float(simpledialog.askstring("Target Amount", "Target Amount (RM):"))
        except:
            messagebox.showerror("Error", "Invalid amount")
            return
        target_date = simpledialog.askstring("Target Date", "Target Date (YYYY-MM-DD):")
        if not target_date:
                messagebox.showwarning("Invalid Input", "Invalid.")
                return
        if not self.valid_date_ymd(target_date):
                messagebox.showwarning("Invalid Input", "Please enter a valid date in YYYY-MM-DD format.")
                return


        goal = self.create_goal(title, target_amount, target_date)
        self.goals.append(goal)
        self.save_goals(self.goals)
        self.refresh_listbox()
        messagebox.showinfo("Success", "Goal added successfully")

    # Add Saving Goal
    def add_saving_to_goal(self):
        if not self.listbox.curselection():
            messagebox.showerror("Error", "Select a goal first")
            return
        index = self.listbox.curselection()[0]
        goal_id = self.goals[index]["id"]
        #Exception Handling 28
        try:
            amount = float(simpledialog.askstring("Add Saving", "Amount to save (RM):"))
        except:
            messagebox.showerror("Error", "Invalid amount")
            return
        note = simpledialog.askstring("Note", "Note:")

        if self.add_saving(self.goals, goal_id, amount, note):
            self.save_goals(self.goals)
            self.refresh_listbox()
            self.show_goal_detail(None)
            
            # Excess warning
            if self.goals[index]["current_amount"] > self.goals[index]["target_amount"]:
                messagebox.showinfo("Notice", "You have exceeded the target amount!")
            else:
                messagebox.showinfo("Success", "Saving added")
        else:
            messagebox.showerror("Error", "Goal not found")

    # Delete Goal
    def delete_selected_goal(self):
        if not self.listbox.curselection():
            messagebox.showerror("Error", "Select a goal first")
            return
        index = self.listbox.curselection()[0]
        goal_id = self.goals[index]["id"]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this goal? This action cannot be undone."):
            if self.delete_goal(self.goals, goal_id):
                self.save_goals(self.goals)
                self.refresh_listbox()
                # Delete Rightside
                for widget in self.detail_frame.winfo_children():
                    widget.destroy()
                tk.Label(self.detail_frame, text="Select a goal", justify="left", font=self.font_main).pack()
                messagebox.showinfo("Deleted", "Goal deleted")
            else:
                messagebox.showerror("Error", "Unable to delete goal")

    def load_goals(self):
        if not os.path.exists(self.SAVINGS_FILE): 
            return []
        #Exception Handling 29
        try:
            with open(self.SAVINGS_FILE, "r", encoding="utf-8") as f: 
                return json.load(f)
        except Exception:
            return []

    def save_goals(self, goals):
        with open(self.SAVINGS_FILE, "w", encoding="utf-8") as f: 
            json.dump(goals, f, indent=4, ensure_ascii=False)

    def create_goal(self, title, target_amount, target_date=None): 
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "target_amount": target_amount,
            "current_amount": 0.0,
            "created_at": date.today().strftime("%d-%m-%Y"),
            "target_date": target_date,
            "history": []
        }

    def add_saving(self, goals, goal_id, amount, note=""):
        for goal in goals:
            if goal["id"] == goal_id:
                goal["current_amount"] += amount
                goal["history"].append({
                    "date": date.today().strftime("%d-%m-%Y"),
                    "amount": amount,
                    "note": note
                })
                return True
        return False

    def delete_goal(self, goals, goal_id):
        before = len(goals)
        goals[:] = [g for g in goals if g["id"] != goal_id]
        return len(goals) < before

    def simple_tax_estimator(self):
        self.clear_active_frames()

        if not hasattr(self, "simple_tax_estimator_frame"):
             # Outer frame within main_content_frame
             self.simple_tax_estimator_frame = Frame(self.main_content_frame, bd=3, relief="raised", padx=10, pady=10, bg="#F9F9F9")

        self.history = load_history()

        if not hasattr(self, "simple_tax_estimator_frame") or not self.simple_tax_estimator_frame.winfo_exists():
             self.simple_tax_estimator_frame = Frame(self.simple_tax_estimator_frame, bg="#F0F0F0")
             self.simple_tax_estimator_frame.pack(fill="both", expand=True)

        self.simple_tax_estimator_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Clear previous content in the page frame (if any)
        for widget in self.simple_tax_estimator_frame.winfo_children():
             widget.destroy()

        input_frame = Frame(self.simple_tax_estimator_frame, bg="#F9F9F9")
        input_frame.pack(pady=10)
        # ---------- Labels ----------
        ttk.Label(self.simple_tax_estimator_frame, text="Simple Tax Estimator", font=("Times New Roman", 16, "bold")).pack(pady=10)

        Label(input_frame, text="Annual Income (RM):", font=("Times New Roman", 12), bg="#F9F9F9").pack(side=LEFT, padx=5)

        self.income_entry = Entry(input_frame, width=20)# Input box for income
        self.income_entry.pack(side=LEFT, padx=5)

        Label(input_frame, text="Deduction (RM):", font=("Times New Roman", 12), bg="#F9F9F9").pack(side=LEFT, padx=5)
        self.deduction_entry = Entry(input_frame, width=20)# Input box for deduction
        self.deduction_entry.insert(0, "")
        self.deduction_entry.pack(side=LEFT, padx=5)

        # ---------- Tax Mode Selection ----------
        ttk.Label(self.simple_tax_estimator_frame, text="Select Tax Method:", font=("Times New Roman", 12)).pack(pady=5)

        self.tax_mode = tk.StringVar(value="progressive")
        ttk.Radiobutton(self.simple_tax_estimator_frame, text="Progressive Tax", variable=self.tax_mode, value="progressive").pack()
        ttk.Radiobutton(self.simple_tax_estimator_frame, text="Flat Rate (10%)", variable=self.tax_mode, value="flat").pack()

        # ---------- Buttons ----------
        ttk.Button(self.simple_tax_estimator_frame, text="Calculate Tax",command=self.calculate_tax,width=20,style="Blue.TButton").pack(pady=12)                   # Button to calculate tax
        ttk.Button(self.simple_tax_estimator_frame, text="View History",command=self.view_history,width=20,style="Green.TButton").pack()                           # Button to show history
        ttk.Button(self.simple_tax_estimator_frame, text="Close", command=self.hide_simple_tax_estimator_frame,width=20,style="Red.TButton").pack(padx=15)

        # ---------- Output Box ----------
        self.output = tk.Text(self.simple_tax_estimator_frame, height=7, width=45, font=("Consolas", 10))  # Display area
        self.output.pack(pady=10)

    def hide_simple_tax_estimator_frame(self):
        """Hides the savings goal tracker frame and returns to the main menu."""
        if hasattr(self, "simple_tax_estimator_frame"):
            self.simple_tax_estimator_frame.pack_forget()
        self.display_main_menu()

    # The builder function is not needed in this layout, but if you keep it:
    def show_simple_tax_estimator_frame(self, builder):
        """Hides previous content in page_frame and calls the builder function."""
        if hasattr(self, "simple_tax_estimator_frame"): 
            for widget in self.simple_tax_estimator_frame.winfo_children():
                widget.destroy()

        # Build the new page content
        builder()

    # ------------------ GUI helper functions ------------------------

    def calculate_tax(self):
        """Validate input → calculate tax → display → save history."""
        #Exception Handling 30
        try:
            income = self.convert_to_safe_float(self.income_entry.get())
            deduction = self.convert_to_safe_float(self.deduction_entry.get())

            # check negative values
            if income < 0 or deduction < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")   # Show error message if input is not valid
            return

        tax, avg_rate = self.tax_calc.calculate_tax(income, deduction)

        # Choose estimator
        if self.tax_mode.get() == "flat":
            estimator = TaxEstimator(0.10)                                  # Flat tax: 10%
        else:
            estimator = TaxEstimator()                                      # Progressive tax

        tax = estimator.calculate_tax(income, deduction)                    # Calculate tax using the chosen estimator
        taxable = max(0, income - deduction)                                # Calculate taxable income (cannot be negative)
        avg_rate = (tax[0] / taxable * 100) if taxable else 0               # Calculate average tax rate (percentage)

        # Display output
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Income: RM {income:,.2f}\n")
        self.output.insert(tk.END, f"Deduction: RM {deduction:,.2f}\n")
        self.output.insert(tk.END, f"Taxable Income: RM {taxable:,.2f}\n")
        self.output.insert(tk.END, f"Estimated Tax: RM {tax[0]:,.2f}\n")
        self.output.insert(tk.END, f"Average Tax Rate: {avg_rate:.1f}%\n")

        # Save to file
        record = {
            "date": date.today().isoformat(),  # Save today’s date
            "income": income,
            "deduction": deduction,
            "tax": tax[0],
            "method": self.tax_mode.get(),
        }

        self.history.append(record)   # Add record to list
        save_history(self.history)    # Save list to JSON file
        messagebox.showinfo("Saved", "Calculation saved to history!")  # Success message

    def view_history(self):
        """Show previous tax calculations."""

        if hasattr(self, 'history_window') and self.history_window.winfo_exists():
            self.history_window.lift() 
            return
        #Exception Handling 31
        try:
            self.history_window = tk.Toplevel(self.window)
        except Exception as e:

            print(f"Error creating Toplevel: {e}")
            return

        self.text_box = tk.Text(self.history_window, font=("Consolas", 10))# Text area to show history
        self.text_box.pack(fill="both", expand=True)

        # If there is no history, show message
        if not self.history:
            self.text_box.insert(tk.END, "No history found.")
        else:
            # Display each saved record
            for r in self.history:
                if isinstance(r['tax'], (list, tuple)):
                    tax_amount = r['tax'][0]
                else:
                    tax_amount = r['tax']
                
                self.text_box.insert(tk.END,
                                    f"{r['date']} | Income RM{r['income']:,.2f} | "
                                    f"Deduction RM{r['deduction']:,.2f} | Tax RM{tax_amount:,.2f} "
                                    f"| Mode: {r['method']}\n")            


if __name__ == "__main__":
    print(f"FinTracker folder: {BASE_DIR}")
    print(f"Login image: {LOGIN_IMAGE_FILE}")
    print(f"Background image: {BACKGROUND_IMAGE_FILE}")
    LoginWindow()
