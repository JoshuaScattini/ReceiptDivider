import customtkinter
from customtkinter import *
from tkinter import *
import tkinter.messagebox
from tkinter import filedialog
import ReceiptReader
from ReceiptReader import *

# Set the appearance mode and default color theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

# Initialize global variables
file1 = None
current_page = "main_menu"  # Change this to the current page you're displaying
file1_placed = None
items = None
total_text_window = None
who_paid = None

# Function to locate receipt file
def find_File():
    global file1
    file_path = filedialog.askopenfilename(initialdir="\Downloads", title="Select a file",
                                           filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")))
    if file_path:
        file_path = file_path.strip()  # Remove extra spaces and whitespace from the file path
        file1 = file_path  # Update the global variable
        update_file_label(file1_placed, file_path)  # Update the label with the selected file path


# Function to calculate costs based on selected items
def calculate_costs(dict1, dict2, dict3):
    def single_costs(d):
        total = 0
        for item, cost in d.items():
            total += cost
        return float(f'{total:.2f}')

    total1 = single_costs(dict1)
    total2 = single_costs(dict2)
    
    total3 = single_costs(dict3)

    return total1, total2, total3

# Function to calculate the total content height based on items
def calculate_total_content_height(itemsBought):
    item_height = 30  # Replace with the actual height of each item
    num_items = len(itemsBought)  # Replace with the actual number of items
    total_height = num_items * item_height
    return total_height

# Function to set up canvas content for the current page
def setup_canvas_content(current_page):
    my_canvas.delete('all')  # Clear existing canvas content
    global file1_placed
    global file1

    if current_page == "main_menu":
        my_canvas.create_image(155, 200, image=Icon_Image, anchor="nw")
        my_canvas.create_text(380, 270, text="Receipt Splitter", font=("Helvetica", 25), fill="black")
        my_canvas.create_text(460, 300, text="the 'First-Day' edition", font=("Helvetica", 8), fill="black")
        my_canvas.create_text(360, 410, text="Select PDF receipt file", font=("Helvetica", 12), fill="black")

        entry1 = customtkinter.CTkButton(master=my_canvas, text="Search Receipt", text_color="black", command=find_File)
        entry1_window = my_canvas.create_window(120, 430, anchor="nw", window=entry1)

        submit1 = customtkinter.CTkButton(master=my_canvas, text="Submit", text_color="black",
                                          command=lambda: submit_click("splitter"))
        submit1_window = my_canvas.create_window(290, 485, anchor="nw", window=submit1)

        # Specify fixed border dimensions
        border_width = 1
        x = 250  # New x-coordinate
        y = 431  # New y-coordinate

        border_x1 = x - border_width
        border_y1 = y - border_width
        border_x2 = x + 330  # Adjust the width as needed
        border_y2 = y + 25  # Adjust the height as needed

        # Create the rectangle at the new position
        border = my_canvas.create_rectangle(border_x1, border_y1, border_x2, border_y2, outline="black",
                                           width=border_width)

        # Create a standard tkinter frame
        file1_frame = Frame(my_canvas)
        file1_placed = customtkinter.CTkLabel(master=file1_frame, text="...", text_color="black", height=1)
        file1_placed.pack()

        # Create a window item for the standard tkinter frame
        file1_window = my_canvas.create_window(270, 436, anchor="nw", window=file1_frame)

    elif current_page == "splitter":
        # Initialize global variables
        global items
        itemsBought, total = grab_items_and_price(file1)
        items = itemsBought

        # Create a variable for spacing between labels and dictionaries for item categorization
        label_spacer = 0
        Shopper_1 = {}
        Shopper_2 = {}
        both = {}
        selected_item = {}

        # Create labels and text on the canvas
        my_canvas.create_text(50, 135, text="Item", font=("Helvetica", 12), fill="black", anchor="w")
        my_canvas.create_text(375, 135, text="Price ($)", font=("Helvetica", 12), fill="black", anchor="w")
        my_canvas.create_text(465, 135, text="Shopper 1", font=("Helvetica", 9), fill="black", anchor="w")
        my_canvas.create_text(550, 135, text="Both", font=("Helvetica", 9), fill="black", anchor="w")
        my_canvas.create_text(605, 135, text="Shopper 2", font=("Helvetica", 9), fill="black", anchor="w")

        # Function to update the selected radio button value
        def update_value(item, value):
            if value == 3:  # shopper2 selected this item
                Shopper_2[item] = itemsBought[item] 
                if item in Shopper_1:
                    del Shopper_1[item]
                if item in both:
                    del both[item]
            elif value == 1:  # shopper1 selected this item
                Shopper_1[item] = itemsBought[item]
                if item in Shopper_2:
                    del Shopper_2[item]
                if item in both:
                    del both[item]
            elif value == 2:  # Both selected this item
                both[item] = itemsBought[item]
                if item in Shopper_2:
                    del Shopper_2[item]
                if item in Shopper_1:
                    del Shopper_1[item]

            # Print the updated item categorization
            print("Shopper 1:", Shopper_1)
            print("Shopper 2:", Shopper_2)
            print("Both:", both)

        # Add all items to the 'both' dictionary initially
        for item, value in itemsBought.items():
            both[item] = value

        # Loop through items and create labels and radio buttons
        for item in itemsBought:
            value = itemsBought[item]

            selected_item[item] = tkinter.IntVar()

            my_canvas.create_text(50, 165 + label_spacer, text=item, font=("Helvetica", 10), fill="black",
                                anchor="w")
            my_canvas.create_text(430, 165 + label_spacer, text=f'${value:.2f}', font=("Helvetica", 10),
                                fill="black", anchor='e')

            radio_button_1 = customtkinter.CTkRadioButton(root, text="", variable=selected_item[item], value=1,
                                                        bg_color='#f0f0f0', command=lambda item=item: update_value(item, 1))
            radio_button_2 = customtkinter.CTkRadioButton(root, text="", variable=selected_item[item], value=2,
                                                        bg_color='#f0f0f0', command=lambda item=item: update_value(item, 2))
            radio_button_3 = customtkinter.CTkRadioButton(root, width=25, text="", variable=selected_item[item], value=3,
                                                        bg_color='#f0f0f0', command=lambda item=item: update_value(item, 3))

            # Place the radio buttons at the specified (x, y) coordinates
            radio_button_1_window = my_canvas.create_window(480, 165 + label_spacer, window=radio_button_1,
                                                            anchor="w")
            radio_button_2_window = my_canvas.create_window(550, 165 + label_spacer, window=radio_button_2,
                                                            anchor="w")
            radio_button_3_window = my_canvas.create_window(620, 165 + label_spacer, window=radio_button_3,
                                                            anchor="w")

            radio_button_2.select()

            label_spacer += 40

        my_canvas.create_text(340, 165 + label_spacer, text='Total: ', font=("Helvetica", 10), fill="black",
                                anchor="w")
        
        my_canvas.create_text(380, 165 + label_spacer, text='$'+total, font=("Helvetica", 10), fill="black",
                                anchor="w")

        label_spacer += 100

        # Calculate the total content height after loading items
        #y = calculate_total_content_height(items)

        # who paid

        my_canvas.create_text(100, label_spacer + 80, text="Who made the payment? ")
        radio_button_4 = customtkinter.CTkRadioButton(root, text="Shopper_1", variable=who_paid, value='Shopper_1',
                                                        bg_color='#f0f0f0', text_color="black")
        
        radio_button_5 = customtkinter.CTkRadioButton(root, text="Shopper_2", variable=who_paid, value='Shopper_2',
                                                        bg_color='#f0f0f0', text_color="black")
        
        radio_button_4_window = my_canvas.create_window(60, label_spacer + 120, window=radio_button_4, anchor="w")
        radio_button_5_window = my_canvas.create_window(60, label_spacer + 160, window=radio_button_5, anchor="w")
        
        
        
        # Create a "Calculate" button
        submit2 = CTkButton(master=my_canvas, text="Calculate", text_color="black",
                            command=lambda: update_total_values(label_spacer, Shopper_2, both, Shopper_1, who_paid))  #

        submit2_window = my_canvas.create_window(60, label_spacer+200, anchor="nw", window=submit2)



        # Adjust label_spacer if needed
        if label_spacer < 700:
            label_spacer = 0
        elif label_spacer >= 700:
            label_spacer -= 700

        canvas_height = label_spacer + 700

        # Set the canvas height
        my_canvas.configure(width=700, height=canvas_height+200)
        e = my_canvas.configure(scrollregion=my_canvas.bbox("all"))
        my_canvas.bind("<Configure>", e)

    my_canvas.update()  # Update the canvas to reflect changes

# Function to update the displayed total values
def update_total_values(label_spacer, shopper_2, both, shopper_1, who_paid):
    global total_text_window
    who_paid_window = None
    total_values = calculate_costs(shopper_2, both, shopper_1)
    total_text = f'Shopper_1: ${total_values[0]:.2f}\tBoth: ${total_values[1]:.2f}\tShopper_2: ${total_values[2]:.2f}'
    
    if who_paid != 'Shopper_2':
        paid_text = f'Shopper_1 owes Shopper_2: ${(total_values[2] + (total_values[1] / 2)):.2f}'
    else:
        paid_text = f'Shopper_2 owes Shopper_1: ${(total_values[0] + (total_values[1]/2)):.2f}'

    if total_text_window:
        my_canvas.delete(total_text_window)
    if label_spacer == 0:
        label_spacer = 350
    else:
        label_spacer += 750
    
    total_text_window = my_canvas.create_text(310, label_spacer,text=total_text, font=("Helvetica", 10), anchor="nw")

    # Update the total values text element
    my_canvas.itemconfig(total_text_window, text=total_text)

    who_paid_window = my_canvas.create_text(360, label_spacer + 100, text=paid_text, font=("Helvetica", 12), anchor='nw')


# Function to update the selected file label
def update_file_label(label, file_path):
    max_length = 46  # Adjust the maximum length as needed
    if len(file_path) > max_length:
        shortened_path = "..." + file_path[-(max_length - 3):] + " "
    else:
        shortened_path = file_path

    # Update the label's associated file path
    label.file_path = file_path
    label.configure(text=shortened_path)

# Function to handle the "Submit" button click
def submit_click(request_page):
    setup_canvas_content(request_page)

# Create the root window
root = customtkinter.CTk()
root.title("Receipt Divider")
root.geometry("700x700")

# Create a scrollable frame
main_frame = CTkScrollableFrame(root)
main_frame.pack(fill="both", expand=TRUE, anchor="center")  # Use anchor="center" to center the frame

# Load Receipt Icon_logo image
Icon_Image = PhotoImage(file="ReceiptDivider\Images\Icon_Split.png")

# Create a canvas
my_canvas = customtkinter.CTkCanvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Create a frame inside the canvas to hold the content
content_frame = Frame(my_canvas)
my_canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Configure canvas dimensions
my_canvas.configure(width=700, height=700)

# Initialize canvas content
setup_canvas_content(current_page)

# Start the main GUI loop
root.mainloop()