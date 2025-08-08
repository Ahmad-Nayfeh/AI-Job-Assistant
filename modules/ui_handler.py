# This module handles all user interface interactions, like printing formatted messages.

def print_header(title):
    """Prints a main header."""
    print("\n" + "="*50)
    print(f" {title.upper()} ".center(50, "="))
    print("="*50)

def print_subheader(title):
    """Prints a sub-header."""
    print("\n" + "-"*50)
    print(f" {title} ".center(50))
    print("-"*50)

def print_success(message):
    """Prints a success message."""
    print(f"  [✔] {message}")

def print_info(message):
    """Prints an informational message."""
    print(f"  [i] {message}")

def print_warning(message):
    """Prints a warning message."""
    print(f"  [!] {message}")

def print_error(message):
    """Prints an error message."""
    print(f"  [✘] ERROR: {message}")

def get_user_choice(config_mode):
    """
    Asks the user to choose the automation mode and explains the options.
    """
    print_subheader("Choose Automation Mode")
    print("Please choose how you want the script to run:")
    print("\n1. REVIEW MODE (Recommended for first-time use)")
    print("   - Step 1: Processes 'Pending' jobs and changes their status to 'Ready to Send'.")
    print("   - Step 2: You manually review the generated emails in the Excel file.")
    print("   - Step 3: You change the status of jobs you like to 'Approved'.")
    print("   - Step 4: Run the script again to send only the 'Approved' emails.")
    
    print("\n2. FULL MODE (Fully Automated)")
    print("   - Processes 'Pending' jobs, generates emails, AND sends them immediately.")
    print("   - Status changes directly from 'Pending' to 'Applied' or 'Failed'.")

    while True:
        default_choice = "1" if config_mode.upper() == 'REVIEW' else "2"
        choice = input(f"\nEnter your choice (1 for REVIEW, 2 for FULL) [Default: {default_choice}]: ").strip()
        
        if not choice:
            choice = default_choice

        if choice == '1':
            print_success("REVIEW mode selected.")
            return 'REVIEW'
        elif choice == '2':
            print_success("FULL mode selected.")
            return 'FULL'
        else:
            print_error("Invalid choice. Please enter 1 or 2.")