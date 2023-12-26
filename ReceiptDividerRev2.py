import fitz  # pip install PyMuPDF
from tkinter import Tk, filedialog  # inbuilt
import time  # inbuilt
import subprocess


class PDFReader():
    """This Class is used to extract data from the PDF and have it ready for other class implementation."""

    def __init__(self, file_location=None, header_rows=4):  # 4 is the header space for woolworths digi recipets
        self.__file_location = file_location
        self.__header_rows = header_rows
        self.__extracted_total = 0.0
        self.__prepped_item_data = None
        self.__digi_receipt = None

    def read_file(self):
        """This function scans the PDF File and returns a list of string values inside a list."""

        doc = fitz.open(self.get_file_location())

        for page in doc:
            text = page.get_text("text")

        # Split the text into lines
        lines = text.split('\n')

        self.identify_item(lines)

    def identify_item(self, unsorted_data_list):
        """This function identifies a single object in the receipt"""
        found_total = False
        items_and_price_list = []
        current_item = ""

        header = self.get_header_rows()

        # Identifying the items and price
        for line in unsorted_data_list[header:]:
            # Break the loop if the line starts with "^Promotional Price"
            if line.strip().startswith("^Promotional Price"):
                break

            # Check if the line ends with spaces and is not a price reduced line
            if line.endswith("  ") and not line.startswith("  PRICE REDUCED"):
                current_item = line.strip()  # Set the current item

            # If the line doesn't end with spaces, it is a new item
            else:
                # If current_item is not empty, it means there's a preceding item
                if current_item:
                    # Concatenate the item and line and append to items_and_price_list
                    items_and_price_list.append(current_item + " " + line.strip())

                    # Reset current_item
                    current_item = ""

                # If it's not a continuation, directly add the line
                else:
                    items_and_price_list.append(line.strip())

        # Check if there's any remaining data in current_item
        if current_item:
            items_and_price_list.append(current_item)

        # Search for the receipt total
        for line in unsorted_data_list[header:]:
            if " TOTAL " in line and not found_total:
                total = self.extract_price(line)
                found_total = True
                self.set_extracted_total(total)

        self.discount_handling(items_and_price_list)

    def discount_handling(self, unprocessed_item_list):
        index = 0
        member_price_saving_indices = []

        while index < len(unprocessed_item_list):
            item_line = unprocessed_item_list[index]

            if item_line.startswith("Member Price Saving"):
                discount = self.extract_discount(item_line)

                # Add the current index to the list of indices to remove
                member_price_saving_indices.append(index)

                # Adjust the previous item's price
                if index > 0:
                    previous_item_line = unprocessed_item_list[index - 1]
                    original_price = self.extract_price(previous_item_line)

                    # If the previous item's price is successfully extracted, adjust it
                    if original_price is not None:
                        new_price = original_price + discount
                        unprocessed_item_list[
                            index - 1] = f"{previous_item_line[:-len(str(original_price)) - 1].rstrip()}{' ' * 6}{new_price:.2f}"

            index += 1

        # After the loop, remove the lines with "Member Price Saving" in reverse order
        for remove_index in sorted(member_price_saving_indices, reverse=True):
            unprocessed_item_list.pop(remove_index)

        # Continue with any remaining logic or method calls
        # for i in unprocessed_item_list:
        #    print(i)

        self.data_prep(unprocessed_item_list)

    def get_extracted_total(self):
        return self.__extracted_total

    def set_extracted_total(self, total):
        self.__extracted_total = total

    def extract_discount(self, line):
        # Extract the discount value from the line
        return float(line.split()[-1])

    def set_digi_receipt(self, item_data=None, receipt_total=None):
        if item_data is None:
            item_data = self.get_prepped_item_data()
        if receipt_total is None:
            receipt_total = self.get_extracted_total()

        self.__digi_receipt = Receipt(item_data, receipt_total)

    def get_digi_receipt(self):
        if self.__digi_receipt is None:
            print("Receipt not set. Receipt is set to NONE.")

        return self.__digi_receipt

    def extract_price(self, line):
        # Extract the price value from the line
        try:
            return float(line.split()[-1].strip("$"))
        except ValueError:
            return None

    def data_prep(self, items_and_prices):

        items_found = []

        for line in items_and_prices:
            # i need to capture the item in the line, item == line until 1st "  "
            space_char_count = 0
            item_name = ""
            item_start = False

            # To extract the item from the line of text
            for char in line:

                if item_start:
                    if char == " ":
                        space_char_count += 1
                    else:
                        space_char_count = 0

                    if space_char_count == 3:
                        break

                    item_name += char

                elif char.isalnum() or char.isspace():

                    if char.isalpha() or char.isdigit():
                        item_start = True

                    if item_start:
                        item_name += char

            item_name = item_name.strip()  # Remove leading and trailing whitespaces

            # to extract the price of the item from the line of text.
            temp_line = ""
            for char in reversed(line):
                if char.isdigit() or char == '.':
                    temp_line += char
                else:
                    break

            item_price = float(temp_line[::-1])

            items_found.append([item_name, item_price])

        self.create_item_dict(items_found)

    def create_item_dict(self, items_found):
        """Logic for creating items using identify_items goes here."""

        items_dict = {}

        for item in items_found:
            temp = GroceryItem(item[0], item[1])
            items_dict[temp.get_id_num()] = temp

        self.set_prepped_item_data(items_dict)

    def set_file_loaction(self, file_location):
        """This function is used to set the file location."""
        self.__file_location = file_location

    def get_file_location(self):
        """This function returns the file location of the PDF receipt file."""
        return self.__file_location

    def set_header_rows(self, header_rows: int):
        """This function sets the number of rows in the receipt that is used for header."""
        self.__header_rows = header_rows

    def get_header_rows(self):
        """This function returns the number of rows occupied by the header."""
        return self.__header_rows

    def get_prepped_item_data(self):
        return self.__prepped_item_data

    def set_prepped_item_data(self, item_dict):
        self.__prepped_item_data = item_dict

    def __str__(self):
        """This function returns a user friendly string representation of the contents of the PDF File"""
        pass

    def __repr__(self):
        """This function returns a list of the items identified within the list."""
        pass


class GroceryItem():
    """This class is used to store the data extracted from the PDF file."""

    next_id = 1

    def __init__(self, item_name: str, item_price: float):
        self.__id_num = GroceryItem.next_id
        GroceryItem.next_id += 1

        self.__item_name = item_name
        self.__item_price = item_price

    def get_id_num(self):
        return self.__id_num

    def get_item_name(self):
        return self.__item_name

    def get_item_price(self):
        return self.__item_price

    def __str__(self):
        """This function returns a interface friendly string of the item."""

        grocery_item_str = f"Product:\t{self.get_item_name()}\nPrice: \t\t" + \
                           f"${self.get_item_price()}\n"

        return grocery_item_str

    def __repr__(self):
        """This function returns the data associated with the item."""
        grocery_item_repr = f"GroceryItem({self.get_id_num()}, '{self.get_item_name()}', {self.get_item_price()})"

        return grocery_item_repr


class Receipt():
    """This class stores the data extracted from the PDF file Class where further processing can be done."""

    def __init__(self, receipt_items, receipt_total):
        self.__receipt_items = receipt_items
        self.__receipt_total = receipt_total

    def get_receipt_items(self):
        return self.__receipt_items

    def get_receipt_total(self):

        receipt_total = 0.0
        for item, obj in self.__receipt_items.items():
            receipt_total += obj.get_item_price()

        formatted_total = f"{receipt_total:.2f}"

        if formatted_total != str(self.__receipt_total):
            print("WARNING!: Receipt does not match calculated total.")

        return formatted_total

    def __str__(self):
        """Returns a friendly representation of the Receipt Class,
        with all the number of items, the name, price and total price of all items."""

        item_num = 1
        return_str = f"Number of items in receipt: {len(self.get_receipt_items())}\n"

        for item, obj in self.get_receipt_items().items():
            return_str += f"Item number: {item_num}\n"
            return_str += str(obj)
            item_num += 1

        return_str += f"\nTotal: ${self.get_receipt_total()}"

        return return_str

    def __repr__(self):
        """Returns the receipt, len of receipt, contents and total price."""

        return_str = f"{len({self.get_receipt_items()})}, " + \
                     f"{', '.join(item.get_item_name() for item in self.get_receipt_items())}, " + \
                     f"{self.get_receipt_total()}"

        return return_str


class Shopper():
    """This class represents a Shopper that has a stake in the receipt to divide."""

    def __init__(self, name, spending_tracker=None):
        self.__name = name
        self.__personal_cart_items = []
        self.__paid = False
        self.__current_cart_total = 0.0

        if spending_tracker is None:
            self.__spending_tracker = 0.0
        else:
            self.__spending_tracker = spending_tracker

    def get_name(self):
        return self.__name

    def get_paid(self):
        return self.__paid

    def set_paid(self, paid=False):
        self.__paid = paid

    def get_current_cart_total(self, setter="n"):
        """This function calculates the total of the current cart.
        Optionally, if the setter parameter is set to "y" it will also store the value."""

        current_cart_total = 0.0
        for item in self.__personal_cart_items:
            current_cart_total += item.get_item_price()

        if setter == "y":
            self.set_current_cart_total(current_cart_total)
        return current_cart_total

    def set_current_cart_total(self, cart_total):
        self.__current_cart_total = cart_total

    def get_personal_cart_items(self):
        return self.__personal_cart_items

    def add_to_peronal_cart(self, item_obj):
        """This function adds a grocery item to the personal cart of the shopper."""

        # Adds the passed item to the personal shoppers cart
        self.__personal_cart_items.append(item_obj)
        print(f"{item_obj.get_item_name()} was added to {self.get_name()}'s cart.")

    def remove_from_personal_cart(self, item_obj):
        """This function removes an item from the personal cart if it is found.
        Additionally, if "x" is passed a parameter, the personal cart is reset."""

        # Handles the scenario when the item is found
        if item_obj in self.__personal_cart_items:
            removed_item = self.__personal_cart_items.remove(item_obj)
            print(f"{removed_item.get_item_name()} was removed from {self.get_name()}'s cart.")

        # Handles the scenario when the item is not found
        elif item_obj not in self.__personal_cart_items:
            print(f"{item_obj.get_item_name()} was not found in {self.get_name()}'s cart")

        # This grants the developer to ability to reset the cart list if they wish to do so.
        elif item_obj == "x":
            self.__personal_cart_items = []

    def calculate_total(self):
        total_cost = 0.0
        for item in self.__personal_cart_items:
            total_cost += item.get_item_price()

        return total_cost

    def get_spending_tracker(self):
        return self.__spending_tracker

    def calculate_new_spending_tracker_value(self, setter="n"):
        '''This function should only be called for saving the shopper data in txt file,
         and before the application is terminated.'''

        updated_value = self.get_spending_tracker() + self.get_current_cart_total()

        return updated_value

    def __str__(self):
        """"""
        shopper_str = f"Name: {self.get_name()}"
        shopper_str += f"Number of items in cart: {len(self.get_personal_cart_items())}"
        for item in self.get_personal_cart_items():
            shopper_str += f"{item.get_item_name()} | {item.get_item_price()}"


class ReceiptDivider():
    """"""

    def __init__(self):
        self.__registered_shoppers = {}
        self.__shoppers_in_receipt = {}
        self.__receipt_file_location = ""
        self.__receipt = None

    def display_menu(self):

        run = True

        display_options = {"d": "Divide Receipt",
                           "r": "Register Shopper",
                           "l": "Show Registered Shoppers",
                           "s": "Scan Receipt",
                           "q": "Quit Program"}

        def select_and_scan_receipt():

            print("Please select digital receipt.")
            time.sleep(0.5)
            self.scan_receipt(self.request_receipt_loaction())

            print("Receipt Scanned.")

        def select_number_of_shoppers():

            correct_input = False

            while not correct_input:  # place in side inner function

                print(f"How many shoppers are splitting this receipt: 1-{len(self.get_registered_shoppers())}")

                try:
                    user_input = int(input(">"))
                except Exception as e:
                    print(e, "Incorrect entry, please use digits only and try again.")

                try:
                    if user_input > len(self.get_registered_shoppers()) or user_input < 1:
                        raise Exception
                    else:
                        correct_input = True
                except Exception as e:
                    print(e, "Number of entered shoppers is out of range.")

            return user_input

        def select_shoppers_names(num_of_shoppers):

            print("Enter the shoppers names.")
            for shopper_num in range(num_of_shoppers):

                correct_input = False
                while not correct_input:

                    print(f"Shopper #{shopper_num + 1}")
                    try:
                        shopper_name = input(">").lower().strip()

                        if shopper_name not in self.get_registered_shoppers():
                            raise Exception
                        else:
                            correct_input = True

                    except Exception as e:
                        print("Shopper not found in registered shoppers.", e)

                self.add_shopper_to_receipt(self.get_registered_shoppers()[shopper_name])

        while run:
            print("Please select from the following options:")
            for option, desc in display_options.items():
                if option == "d" and len(self.get_registered_shoppers()) <= 1:
                    print(f'\t({option}) {desc} (*Requires at least 2 registered shoppers*)')
                else:
                    print(f'\t({option}) {desc}')
            selection = input("> ").lower().strip()

            if selection.lower() not in display_options:
                raise Exception("INCORRECT_INPUT", "Please Enter for one of the options provided.")

            else:
                if selection == "l":
                    self.show_registered_shoppers()

                elif selection == "r":
                    self.create_new_shopper()

                elif selection == "d":

                    correct_input_parameters = ["y", "n", "x"]
                    correct_receipt = False

                    while not correct_receipt:

                        select_and_scan_receipt()
                        print(self.get_receipt())  ## new function to s
                        subprocess.run(['cmd', '/c', f'echo {print(self.get_receipt())} & pause'], shell=True)
                        print("Is this the correct receipt? (y/n) or (x) to return to menu.")

                        correct_input = False
                        while not correct_input:
                            try:
                                user_input = input(">").lower().strip()

                                if user_input not in correct_input_parameters:
                                    raise ValueError("Invalid input. Please enter 'y' or 'x'.")

                                if user_input == "y":
                                    correct_receipt = True
                                    correct_input = True
                                elif user_input == "x":
                                    break
                                else:
                                    correct_input = True

                            except ValueError as e:
                                print(str(e))

                        if user_input == "n":
                            try:
                                print("Would you like to select another receipt? (y) or (n/x) to return to menu.")
                                user_input = input(">")

                                if user_input not in correct_input_parameters:
                                    raise ValueError("Invalid input. Please enter 'y', 'n' or 'x'.")

                                if user_input == "y":
                                    continue
                                else:
                                    user_input = "x"
                                    break

                            except ValueError as e:
                                print(str(e))

                        # Additional indentation is required for the following block
                        if user_input != "x":
                            number_of_shoppers = select_number_of_shoppers()
                            select_shoppers_names(number_of_shoppers)
                        else:
                            pass

                    # prombt to continue

                    # create a new shopper if 2 / Shopper("Both") else/ Shopper("All")
                    # add Shopper to receipt shoppers
                    # For loop assigning all items to Shopper

                    # self.divid_receipt()



                elif selection == "q":
                    run = False
                    self.quit_program()

                elif selection == "s":

                    select_and_scan_receipt()

                    # possible probt to commence. 

                    # split receipt
                    # add method of display to choose which items belong to who.
                    # loop through items, and pick who to asign to.
                    #
                    # add functionality to shoppers to add, remove items from cart.

                    # prombt for who paid.

                    # determine owings

                    # reset neccesary attributes

                    # loop to exit program and ensure everything saves correctly.

    def request_receipt_loaction(self):
        root = Tk()
        root.withdraw()  # Hide the main window
        path = filedialog.askopenfilename(initialdir="\\Downloads", title="Select a file",
                                          filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")))

        return path

    def set_receipt(self, digi_receipt):
        self.__receipt = digi_receipt

    def get_receipt(self):
        return self.__receipt

    def get_receipt_file_loaction(self):
        return self.__receipt_file_loaction

    def set_recipet_file_location(self, file_address):
        self.__receipt_file_loaction = file_address

    def get_registered_shoppers(self):
        return self.__registered_shoppers

    def set_registered_shoppers(self, shopper_dict):
        self.__registered_shoppers = shopper_dict

    def add_registered_shopper(self, shopper):
        self.__registered_shoppers[shopper.get_name()] = shopper

    def get_shoppers_from_receipt(self):
        return self.__shoppers_in_receipt

    def add_shopper_to_receipt(self, shopper):
        self.__shoppers_in_receipt[shopper.get_name()] = shopper

    def set_shoppers_dict_to_receipt(self, shopper_dict):

        if shopper_dict == "x":
            self.__shoppers_in_receipt = {}
        else:
            self.__shoppers_in_receipt = shopper_dict

    def remove_shopper_from_receipt(self, shopper):
        self.__shoppers_in_receipt.pop(shopper)

    def greeting(self):
        '''A freindly greeting for the user.'''

        print("\nWelcome to the Receipt Divider!")
        print("Designed and Produced by Joshua Scattini\n")

    def retreive_existing_shoppers(self, file_name="shoppers.txt"):

        try:
            with open(file_name, 'r') as file:
                for line in file:
                    shopper_data = line.strip("\n").split(',')
                    self.add_registered_shopper(
                        Shopper(str(shopper_data[0]),  # Using the Shopper class, the shopper name is set
                                float(shopper_data[1])))  # Using the Shopper class, the shopper spending tracker is set
        except Exception as e:
            self.set_shoppers_dict_to_receipt("x")
            print("CORRUPT_SHOPPER_DATA: The saved shopper was unable to be retrieved.")

    def create_new_shopper(self):

        valid_input = False
        while not valid_input:
            print("\nPlease enter new shopper's name:\n*'x' to return to menu.*\n")
            user_input = input("<").lower().strip()

            if user_input in self.get_registered_shoppers():
                print("Shopper with that name already exists.")

            elif user_input == 'x':
                valid_input = True

            else:
                self.add_registered_shopper(Shopper(user_input))
                print(f"Welcome, {user_input.capitalize()}!")
                valid_input = True

    def scan_receipt(self, file_location):

        scanner = PDFReader()
        scanner.set_file_loaction(file_location)
        scanner.read_file()
        scanner.set_digi_receipt()
        digi_receipt = scanner.get_digi_receipt()

        self.set_receipt(digi_receipt)

    def divide_receipt(self):

        # get counter and create an index while loop so can cycle, go back, forward, etc. 
        # for loop for each itemg

        # should look like this 

        # (q) to go back to previous item, (w) to go to next item, 
        # (x) to exit back to menu, (v) calculate owings <- will prombt for who paid

        # (item 1 of 30)
        # item name
        # item price

        # Who will take this item
        # (a) shopper.get_name \t (s) shopper.get_name \t (e) shopper("all")

        # currently with shopper(xyz)

        # >

        pass

    def calculate_owings(self):

        # prombt for who paid

        # calculate owings.

        # Show owing calculation result
        # confirm / prombt to complete

        # adjust shoppers trackers, paid.
        pass

    def show_registered_shoppers(self):
        ''''''
        shopper_index = 1
        if len(self.get_registered_shoppers()) == 0:
            print("There are no registered shoppers.")

        else:
            print("\nRegistered Shoppers: ")
            for shopper in self.get_registered_shoppers().values():
                print(f"{shopper_index}. {shopper.get_name().capitalize()}")
                shopper_index += 1
            print('')

    def store_shoppers_details(self, file_name="shoppers.txt"):
        '''This function is responsible for saving the shopper data to the allocated text file.'''

        if len(self.get_registered_shoppers()) != 0:
            with open(file_name, 'w') as file:
                for name, shopper_obj in self.get_registered_shoppers().items():
                    file.write(f'{name},' \
                               f'{shopper_obj.get_spending_tracker()}\n')
        else:
            pass

    def run(self):

        self.greeting()
        self.retreive_existing_shoppers()
        self.display_menu()

    def quit_program(self):
        self.store_shoppers_details()
        print("Good Bye!")


# test = PDFReader()
# test.set_file_loaction("eReceipt_5799_Mawson20Lakes_21Oct2023__wauau.pdf")
# test.read_file()
# test.set_digi_receipt()
# testdigi = test.get_digi_receipt()
##print(testdigi)

receipt_divider = ReceiptDivider()
receipt_divider.run()
