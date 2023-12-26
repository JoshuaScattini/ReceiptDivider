import os
import fitz  # pip install PyMuPDF
from tkinter import Tk, filedialog  # inbuilt
import time  # inbuilt


class PDFReader():
    """
    Class used to extract data from the PDF and prepare it for further implementation.

    Attributes:
    - __file_location (str): File location of the PDF receipt file.
    - __header_rows (int): Number of rows in the receipt used for the header.
    - __extracted_total (float): Extracted total from the PDF receipt.
    - __everyday_extra_discount (float): Everyday Extra Discount applied to the receipt.
    - __prepped_item_data (dict): Prepped data of grocery items extracted from the PDF.
    - __digi_receipt (Receipt): Receipt object created from the extracted data.

    Methods:
    - read_file: Extracts text data from the PDF and identifies items and discounts.
    - identify_item: Identifies a single object (item or discount) in the receipt.
    - discount_handling: Handles discounts in the unprocessed item list.
    - get_extracted_total: Retrieves the extracted total from the PDF receipt.
    - set_extracted_total: Sets the extracted total.
    - extract_discount: Extracts the discount value from a line.
    - set_digi_receipt: Sets the Digi Receipt object.
    - get_digi_receipt: Retrieves the Digi Receipt object.
    - extract_price_or_discount: Extracts the price value from a line.
    - data_prep: Prepares data by extracting items and prices.
    - create_item_dict: Creates a dictionary of grocery items from the identified data.
    - set_file_location: Sets the file location of the PDF receipt file.
    - get_file_location: Retrieves the file location of the PDF receipt file.
    - set_header_rows: Sets the number of rows in the receipt used for the header.
    - get_header_rows: Retrieves the number of rows occupied by the header.
    - get_prepped_item_data: Retrieves the prepped data of grocery items.
    - set_prepped_item_data: Sets the prepped data of grocery items.
    - get_everyday_extra_discount: Retrieves the Everyday Extra Discount applied to the receipt.
    - set_everyday_extra_discount: Sets the Everyday Extra Discount.
    - __str__: Returns a user-friendly string representation of the contents of the PDF File.
    - __repr__: Returns a list of the items identified within the list.
    """

    def __init__(self, file_location=None, header_rows=4):  # 4 is the header space for woolworths digi recipets
        """
        Initializes the PDFReader object.

        Parameters:
        - file_location (str): File location of the PDF receipt file.
        - header_rows (int): Number of rows in the receipt used for the header.
        """
        
        self.__file_location = file_location
        self.__header_rows = header_rows
        self.__extracted_total = 0.0
        self.__everyday_extra_discount = 0.0
        self.__prepped_item_data = None
        self.__digi_receipt = None
        

    def read_file(self):
        """
        Reads and extracts text data from the PDF file. Identifies items and discounts, then passes the data to the `identify_item` method.

        Note:
        This method updates the internal state by identifying items and discounts from the PDF text.
        """

        doc = fitz.open(self.get_file_location())

        for page in doc:
            text = page.get_text("text")

        # Split the text into lines
        lines = text.split('\n')

        # Identify the items and discounts
        self.identify_item(lines)

    def identify_item(self, unsorted_data_list):
        """
        Identifies a single object in the receipt from the given unsorted data list.

        Args:
        - unsorted_data_list (list): List of strings containing unsorted data from the PDF.

        Note:
        This method updates the internal state by setting the extracted total and performs discount handling.
        """

        found_total = False
        items_and_price_list = []
        current_item = ""

        # Identifying the items and price
        for line in unsorted_data_list[self.get_header_rows():]:
            
            # Break the loop if the line starts with "^Promotional Price" or "SUBTOTAL" 
            if "SUBTOTAL" in line or "^Promotional Price" in line:
                break

            # Check if the line ends with spaces and is not a price reduced line
            if line.endswith("  ") and not line.strip().startswith("PRICE REDUCED"):
                current_item = line.strip()  # Set the current item

            # Check if the line starts with "PRICE REDUCED"
            elif line.strip().startswith("PRICE REDUCED"):
                pass

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
        for line in unsorted_data_list[self.get_header_rows():]:
            if " TOTAL " in line and not found_total:
                total = self.extract_price_or_discount(line)
                found_total = True
                self.set_extracted_total(total)

        # Perform discount handling
        self.discount_handling(items_and_price_list)

    def discount_handling(self, unprocessed_item_list):
        """
        Processes and adjusts item prices based on discounts found in the unprocessed item list.

        Args:
        - unprocessed_item_list (list): A list of strings containing unprocessed item information.

        Note:
        This method modifies the input list by adjusting item prices based on discounts. It also updates the everyday extra discount.
        """
        
        index = 0
        item_line_to_remove = []

        # Loop through the list
        while index < len(unprocessed_item_list):
            item_line = unprocessed_item_list[index]

            # Logic if line only contains additional pricing data and not item data
            if item_line.startswith("Member Price Saving") or item_line.startswith("Everyday Extra Discount") or "OFFER" in item_line:
                
                # Extract the discount value
                discount = self.extract_price_or_discount(item_line)
                
                # Add the current index to the list of indices to remove
                item_line_to_remove.append(index)

                # Logic for 'members price saving' or 'OFFER'
                if item_line.startswith("Member Price Saving") or "OFFER" in item_line:

                    # Adjust the previous item's price
                    if index > 0:
                        previous_item_line = unprocessed_item_list[index - 1]
                        original_price = self.extract_price_or_discount(previous_item_line)

                        # If the previous item's price is successfully extracted, adjust it
                        if original_price is not None:
                            new_price = original_price + discount
                            unprocessed_item_list[
                                index - 1] = f"{previous_item_line[:-len(str(original_price)) - 1].rstrip()}{' ' * 6}{new_price:.2f}"
                            
                # Logic for 'Everyday Extra Discount' 
                elif item_line.startswith("Everyday Extra Discount"):           
                    self.set_everyday_extra_discount(discount)

            index += 1

        # After the loop, remove the lines with "Member Price Saving" in reverse order
        for remove_index in sorted(item_line_to_remove, reverse=True):
            unprocessed_item_list.pop(remove_index)

        # Remove the lines with "Everyday Extra Discount"
        self.data_prep(unprocessed_item_list)

    def get_extracted_total(self):
        """Returns the extracted total."""
        return self.__extracted_total

    def set_extracted_total(self, total):
        """Sets the extracted total"""
        self.__extracted_total = total

    def extract_discount(self, line):
        """Extracts the line discount"""

        return float(line.split()[-1])

    def set_digi_receipt(self):
        """Sets the Digi Receipt object."""

        # Extract the nessassary parameters for the Receipt object
        item_data = self.get_prepped_item_data()
        receipt_total = self.get_extracted_total()
        discount = self.get_everyday_extra_discount()

        # Create the Receipt object
        self.__digi_receipt = Receipt(item_data, receipt_total, discount)

    def get_digi_receipt(self):
        """Returns the Digi Receipt object."""
        
        if self.__digi_receipt is None:
            print("Receipt not set. Receipt is set to NONE.")

        return self.__digi_receipt

    def extract_price_or_discount(self, line):
        """
        Extracts the price/discount value from a line.

        Parameters:
        - line (str): Line of text containing price information.

        Returns:
        - float: Extracted price value.
        """
        # Extract the price from the line
        try:
            return float(line.split()[-1].strip("$"))
        except ValueError:
            return None

    def data_prep(self, items_and_prices):
        """
        Processes raw item data and creates a dictionary of GroceryItem objects.

        Args:
        - items_and_prices (list): A list of strings containing raw item information.

        Note:
        This method extracts item names and prices from the input list and creates GroceryItem objects.
        The resulting dictionary is set as the prepped item data for further processing.
        """

        items_found = []

        # Extract the item name and price from each line
        for line in items_and_prices:
            # i need to capture the item in the line, item == line until 1st "  "
            space_char_count = 0
            item_name = ""
            item_start = False

            # To extract the item from the line of text
            for char in line:

                # To check if the item has started
                if item_start:
                    if char == " ":
                        space_char_count += 1
                    else:
                        space_char_count = 0

                    if space_char_count == 3:
                        break

                    item_name += char

                # To check if the item has started
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

            # Reverse the string and convert to float
            item_price = float(temp_line[::-1])

            # Append the item name and price to the list
            items_found.append([item_name, item_price])

        # Create a dictionary of GroceryItem objects
        self.create_item_dict(items_found)

    def create_item_dict(self, items_found):
        """
        Creates a dictionary of grocery items from the identified data.

        Parameters:
        - items_found (list): List of identified grocery items.
        """

        items_dict = {}
        item_key = 1

        # Create a dictionary of GroceryItem objects
        for item in items_found:
            items_dict[item_key] = GroceryItem(item[0], item[1])
            item_key += 1

        # Set the prepped item data
        self.set_prepped_item_data(items_dict)

    def set_file_loaction(self, file_location):
        """Sets the file location of the PDF receipt file."""

        self.__file_location = file_location

    def get_file_location(self):
        """Retrieves the file location of the PDF receipt file."""
        
        return self.__file_location

    def set_header_rows(self, header_rows: int):
        """Sets the number of rows in the receipt used for the header."""

        self.__header_rows = header_rows

    def get_header_rows(self):
        """Retrieves the number of rows occupied by the header."""

        return self.__header_rows

    def get_prepped_item_data(self):
        """Retrieves the prepped data of grocery items."""
        
        return self.__prepped_item_data

    def set_prepped_item_data(self, item_dict):
        """Sets the prepped data of grocery items."""

        self.__prepped_item_data = item_dict

    def get_everyday_extra_discount(self):
        """Retrieves the Everyday Extra Discount applied to the receipt."""

        return self.__everyday_extra_discount
    
    def set_everyday_extra_discount(self, discount):
        """Sets the Everyday Extra Discount."""

        self.__everyday_extra_discount = discount

    def __str__(self):
        '''Returns a user-friendly string representation of the contents of the PDF File.'''
        
        return f"PDFReader(file_location={self.get_file_location()}, header_rows={self.get_header_rows()}, " \
               f"extracted_total={self.get_extracted_total()}, everyday_extra_discount={self.get_everyday_extra_discount()})"

    def __repr__(self):
        """Returns a list of the items identified within the list."""
        
        item_data = self.get_prepped_item_data()
        items_repr = [f"{item.get_name()}: ${item.get_price():.2f}" for item in item_data.values()] if item_data else "None"
        return f"PDFReader(items={items_repr})"


class GroceryItem():
    """
    Class used to store data extracted from a PDF file.

    Attributes:
    - next_id (int): Class variable to assign unique IDs to grocery items.
    - __id_num (int): ID number of the grocery item.
    - __item_name (str): Name of the grocery item.
    - __item_price (float): Price of the grocery item.

    Methods:
    - get_id_num: Get the ID number of the grocery item.
    - get_item_name: Get the name of the grocery item.
    - get_item_price: Get the price of the grocery item.
    - set_item_price: Adjust the price of the grocery item.
    - __str__: Return an interface-friendly string of the item.
    - __repr__: Return the data associated with the item.
    """

    # Class variable to assign unique IDs to grocery items
    next_id = 1

    def __init__(self, item_name: str, item_price: float):
        """
        Initialize the GroceryItem object.

        Parameters:
        - item_name (str): Name of the grocery item.
        - item_price (float): Price of the grocery item.
        """
        
        # Assign a unique ID to the grocery item
        self.__id_num = GroceryItem.next_id
        GroceryItem.next_id += 1

        self.__item_name = item_name
        self.__item_price = item_price

    def get_id_num(self):
        """Returns the itemID of the item."""
        
        return self.__id_num

    def get_item_name(self):
        """Returns the name of the item."""

        return self.__item_name

    def get_item_price(self):
        """"Returns the price of the item."""
        
        return self.__item_price
    
    def set_item_price(self, new_price):
        """Sets the price of the grocery item."""

        self.__item_price = new_price

    def __str__(self):
        '''Return an interface-friendly string of the item.'''

        grocery_item_str = f"Product:\t{self.get_item_name()}\nPrice: \t\t" + \
                           f"${self.get_item_price():.2f}\n"

        return grocery_item_str

    def __repr__(self):
        '''Return the data associated with the item.'''
        grocery_item_repr = f"GroceryItem({self.get_id_num()}, '{self.get_item_name()}', {self.get_item_price()})"

        return grocery_item_repr


class Receipt():
    """
    Class storing data extracted from a PDF file for further processing.

    Attributes:
    - __receipt_items (dict): Dictionary of receipt items.
    - __receipt_total (float): Total cost of items in the receipt.
    - __everyday_extra_discount (float): Extra discount applied to items if specified.

    Methods:
    - recalculate_receipt_total: Recalculate the total cost of items in the receipt.
    - get_everyday_extra_discount: Get the everyday extra discount applied.
    - __str__: Return a friendly representation of the Receipt class.
    - __repr__: Return a string representation of the Receipt class.
    """

    def __init__(self, receipt_items, receipt_total, applied_discount=False):
        """
        Initialize the Receipt object.

        Parameters:
        - receipt_items (dict): Dictionary of receipt items.
        - receipt_total (float): Total cost of items in the receipt.
        - applied_discount (float): Extra discount applied to items if specified.
        """
        
        self.__receipt_items = receipt_items
        self.__receipt_total = receipt_total
        
        # Checks to see if a discount was applied to the receipt
        if applied_discount == False:
            self.__everyday_extra_discount = 0.0
        
        # If a discount was applied, it is set
        else:
            
            print("Discount found!")
            self.__everyday_extra_discount = applied_discount
            
            # Apply the discount to the receipt items
            for item in self.get_receipt_items().values():  
                
                # Checks to see if the item is a giftcard
                if "Giftcard" not in item.get_item_name():
                    discounted_price = float("%.2f" % (item.get_item_price() * 0.9))
                    item.set_item_price(discounted_price)

    def get_receipt_items(self):
        """Returns the items inside the receipt."""
        
        return self.__receipt_items

    def get_receipt_total(self):
        """Returns the receipt total."""
        
        return self.__receipt_total
    
    def get_everyday_extra_discount(self):
        """Get the everyday extra discount applied."""

        return self.__everyday_extra_discount 
    
    def recalculate_receipt_total(self):
        """Recalculate the total cost of items in the receipt.

        Returns:
        - str: Formatted total cost of items in the receipt."""
        
        # Recalculate the receipt total
        receipt_total = 0.0
        for item, obj in self.__receipt_items.items():
            receipt_total += obj.get_item_price()

        formatted_total = f"{receipt_total:.2f}"

        return formatted_total

    def __str__(self):
        '''
        Returns a friendly representation of the Receipt Class.
        '''

        boarder = "=================================="
        item_num = 1

        return_str = f"\n{boarder*2}\n"
        return_str += f"Number of items in receipt: {len(self.get_receipt_items())}\n"

        # Loop through the receipt items and add them to the return string
        for item, obj in self.get_receipt_items().items():
            return_str += f"\nItem number: {item_num}\n"
            return_str += str(obj)
            item_num += 1

        return_str += f"\nTotal: ${float('%.2f' % (self.get_receipt_total()-self.get_everyday_extra_discount()))}\n"

        # Check if an everyday extra discount was applied, and alters sting accordingly
        if self.get_everyday_extra_discount() != 0.0:
            return_str += f"\nAfter Everyday Extra Discount of ${-self.get_everyday_extra_discount()} is applied, " +\
            f"new total is: ${self.recalculate_receipt_total()}.\n"

        return_str += f"{boarder*2}"

        return return_str

    def __repr__(self):
        '''
        Return a string representation of the Receipt class.
        '''
        
        # Loop through the receipt items and add them to the return string
        return_str = f"{len({self.get_receipt_items()})}, " + \
                     f"{', '.join(item.get_item_name() for item in self.get_receipt_items())}, " + \
                     f"{self.get_receipt_total()}"
        
         # Check if an everyday extra discount was applied, and alters sting accordingly
        if self.get_everyday_extra_receipt() != 0.0:
            return_str += f", {self.get_everyday_extra_receipt()}, " +\
                        f"{self.get_receipt_total()-self.get_everyday_extra_receipt()}"

        return return_str


class Shopper():
    '''
    Class representing a shopper with a stake in dividing a receipt.

    Attributes:
    - __name (str): The name of the shopper.
    - __personal_cart_items (list): List of grocery items in the shopper's personal cart.
    - __paid (bool): Indicates if the shopper has paid their share.
    - __cart_total (float): Total cost of items in the shopper's cart.
    - __main_shopping_cart (bool): Flag indicating if the cart is the main shopping cart.
    - __spending_tracker (float): Tracker for the shopper's spending.

    Methods:
    - add_to_personal_cart: Add a grocery item to the shopper's personal cart.
    - remove_from_personal_cart: Remove an item from the personal cart or reset the cart if specified.
    - calculate_cart_total: Calculate the total cost of items in the shopper's cart.
    - calculate_new_spending_tracker_value: Calculate the updated spending tracker value.
    - __str__: Return a string representation of the shopper.
    '''

    def __init__(self, name, spending_tracker=0.0, main_shopping_cart=False, cart_items=None):
        '''Initialize the Shopper object.'''
        
        self.__name = name
        self.__personal_cart_items = cart_items or []
        self.__paid = False
        self.__cart_total = 0.0
        self.__main_shopping_cart = main_shopping_cart
        self.__spending_tracker = spending_tracker or 0.0

    def get_name(self):
        '''Returns the name of the shopper.'''
        return self.__name

    def get_paid(self):
        '''Returns the paid boolean of the shopper.'''
        
        return self.__paid

    def set_paid(self, paid=False):
        '''Sets the paid boolean of the shopper.'''

        self.__paid = paid

    def get_cart_total(self):
        '''Returns the cart total of the shopper.'''
        
        return self.__cart_total

    def set_cart_total(self, cart_total):          
        '''Sets the cart total of the shopper.'''
        
        self.__cart_total = cart_total


    def get_personal_cart_items(self):
        '''Returns the cart items allocated to the shopper.'''
        
        return self.__personal_cart_items

    def add_to_personal_cart(self, item_obj):
        '''
        Add a grocery item to the shopper's personal cart.

        Parameters:
        - item_obj: Grocery item object to be added.
        '''

        # Adds the passed item to the personal shoppers cart
        self.__personal_cart_items.append(item_obj)
        print(f"{item_obj.get_item_name()} was added to {self.get_name()}'s cart.")

    def remove_from_personal_cart(self, item_obj):
        '''
        Remove an item from the personal cart or reset the cart if specified.

        Parameters:
        - item_obj: Grocery item object to be removed. 
          If "x" is passed, the personal cart is reset.
        '''
        
        # Handles the scenario when the item is found
        if item_obj in self.__personal_cart_items:
            removed_item = item_obj
            self.__personal_cart_items.remove(item_obj)
            print(f"{removed_item.get_item_name()} was removed from {self.get_name().capitalize()}'s cart.")

        # Handles the scenario when the item is not found
        elif item_obj not in self.__personal_cart_items:
            print(f"{item_obj.get_item_name()} was not found in {self.get_name().capitalize()}'s cart")

        # This grants the developer to ability to reset the cart list if they wish to do so.
        elif item_obj == "x":
            self.__personal_cart_items = []
        else:
            print("error")

    def calculate_cart_total(self, setter="n"):
        '''
        Calculate the total cost of items in the shopper's cart.

        Parameters:
        - setter (str): If set to "y", the cart total is stored.

        Returns:
        - float: Total cost of items in the shopper's cart.
        '''

        current_cart_total = 0.0
        
        # Loop through the shoppers cart and add the price of each item to the current cart total
        for item in self.__personal_cart_items:
            current_cart_total += item.get_item_price()

        # If the setter is set to "y", the cart total is stored
        if setter == "y":
            self.set_cart_total(current_cart_total)
        
        return current_cart_total

    def get_spending_tracker(self):        
        '''Returns the spending tracker of the shopper.'''
        
        return self.__spending_tracker
    
    def set_spending_tracker(self, spending_tracker):
        '''Sets the spending tracker of the shopper.'''
        
        self.__spending_tracker = spending_tracker
    

    def calculate_new_spending_tracker_value(self, setter="n"):
        '''
        Calculate the updated spending tracker value.

        Parameters:
        - setter (str): If set to "y", the spending tracker is updated.

        Returns:
        - float: Updated spending tracker value.
        '''

        updated_value = self.get_spending_tracker() + self.get_cart_total()

        return updated_value

    def __str__(self):
        '''
        Return a string representation of the shopper.

        Returns:
        - str: String representation of the shopper.
        '''

        shopper_str = f"Name: {self.get_name()}"
        shopper_str += f"Number of items in cart: {len(self.get_personal_cart_items())}"
        for item in self.get_personal_cart_items():
            shopper_str += f"{item.get_item_name()} | {item.get_item_price()}"

    def __str__(self):
        '''
        Return a string representation of the shopper.

        Returns:
        - str: String representation of the shopper.
        '''

        # Basic information about the shopper
        shopper_info = f"Shopper: {self.get_name()}\n"
        
        # Personal cart items
        cart_items_info = "Personal Cart Items:\n"
        for item in self.get_personal_cart_items():
            cart_items_info += f"{item.get_item_name()} | ${item.get_item_price():.2f}\n"

        # Cart total and spending tracker
        cart_total_info = f"Cart Total: ${self.calculate_cart_total():.2f}\n"
        spending_tracker_info = f"Spending Tracker: ${self.calculate_new_spending_tracker_value():.2f}"

        # Constructing the final representation string
        shopper_str = f"{shopper_info}{cart_items_info}{cart_total_info}{spending_tracker_info}"

        return shopper_str

    def __repr__(self):
        '''
        Returns a string representation of the shopper.

        Returns:
        - str: String representation of the shopper.
        '''

        # Creating a list of strings, each representing a grocery item in the personal cart
        cart_items_repr = [f"{item.get_item_name()} | {item.get_item_price()}" for item in self.get_personal_cart_items()]

        # Joining the list items with a newline for better readability
        cart_items_str = "\n".join(cart_items_repr)

        # Constructing the final representation string
        shopper_repr = f"Shopper(name={self.get_name()}, spending_tracker={self.get_spending_tracker()}, " \
                    f"main_shopping_cart={self.__main_shopping_cart}, paid={self.__paid}, " \
                    f"cart_total={self.__cart_total})\nPersonal Cart Items:\n{cart_items_str}"

        return shopper_repr


class ReceiptDivider():
    '''Class for managing the division of a receipt among registered shoppers.

        Attributes:
        - __registered_shoppers (dict): Dictionary to store registered shoppers.
        - __shoppers_in_receipt (dict): Dictionary to store shoppers in the current receipt.
        - __receipt_file_location (str): File location of the current receipt.
        - __receipt: Digital receipt object.

        Methods:
        - display_menu: Display the main menu and handle user input for various options.
        - request_receipt_loaction: Open a file dialog to request the location of a receipt file.
        - greeting: Print a friendly greeting for the user.
        - retreive_existing_shoppers: Retrieve and load existing shopper data from a file.
        - create_new_shopper: Create a new shopper and add them to the list of registered shoppers.
        - scan_receipt: Scan a receipt file and set the digital receipt for further processing.
        - divide_receipt: Divide the items in the current receipt among the shoppers.
        - calculate_owings: Calculate the amount owed by each shopper and display the results.
        - show_registered_shoppers: Display the list of registered shoppers.
        - store_shoppers_details: Store the details of registered shoppers in a file.
        - run: Run the main program, including greetings, data retrieval, and displaying the menu.
        - quit_program: Quit the program and store shopper details before exiting.
        '''

    def __init__(self):
        '''Initialize the ReceiptDivider object.'''

        self.__registered_shoppers = {}
        self.__shoppers_in_receipt = {}
        self.__receipt_file_location = ""
        self.__receipt = None

    def display_menu(self):
        '''Display the main menu and handle user input for various options.'''

        # Dictionary of menu options
        display_options = {"d": "Divide Receipt",
                           "r": "Register Shopper",
                           "l": "Show Registered Shoppers",
                           "s": "Scan Receipt",
                           "q": "Quit Program"}

            ### Private functions for display Menu

        # Prombt for and scan the selected receipt
        def select_and_scan_receipt():
            '''Display Menu private function - Prombts for and scans the selected receipt.'''
            print("Please select digital receipt.")
            time.sleep(0.25)
            self.scan_receipt(self.request_receipt_loaction())

            print("Receipt Scanned.")

        # Prombt for how many shoppers to divide the receipt with, an returns a int value.
        def select_number_of_shoppers():
            '''Display Menu private function - Prombts for how many shoppers to divide the receipt with, an returns a int value.'''

            correct_input = False

            while not correct_input: 
                
                # Min of 2 shoppers is required
                if len(self.get_registered_shoppers()) == 2:
                       return 2

                # If more then 2 shoppers are registered, the user is prombted to select how many shoppers to split receipt.  
                else:
                    print(f"How many shoppers are splitting this receipt: 2-{len(self.get_registered_shoppers())}")

                    try:
                        user_input = int(input(">"))
                    except Exception as e:
                        print(e, "Incorrect entry, please use digits only and try again.")

                    try:
                        if user_input > len(self.get_registered_shoppers()) or user_input <= 1:
                            raise Exception
                        else:
                            correct_input = True
                    except Exception as e:
                        print(e, "Number of entered shoppers is out of range.")

            return user_input

        # Prombt for shoppers names and adds them to the receipt.
        def select_shoppers_names(num_of_shoppers):
            '''Display Menu private function - Prombts for shoppers names.'''

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

                # Adds the shopper to the receipt
                self.add_shopper_to_receipt(self.get_registered_shoppers()[shopper_name])
        

            ### Build and Display Menu 
                
        run = True
        while run:

            # Build menu options 
            print("Please select from the following options:")
            for option, desc in display_options.items():
                
                # Condition if not enough registered shoppers to divid receipt, min 2.
                if option == "d" and len(self.get_registered_shoppers()) <= 1:
                    print(f'\t({option}) {desc} (*Requires at least 2 registered shoppers*)')
                else:
                    print(f'\t({option}) {desc}')

            try:

                # prombt for option
                selection = input("> ").lower().strip()

                # Raise execption if user input doesnt match any of the provided options. 
                if selection.lower() not in display_options:
                    raise Exception("INCORRECT_INPUT", "Please enter for one of the options provided.")
                
            except Exception as e:
                print(e, "\n")

            else:
                
                # Show registered shoppers
                if selection == "l":
                    self.show_registered_shoppers()

                # Create and register new shopper
                elif selection == "r":
                    self.create_new_shopper()

                # Quit Program
                elif selection == "q":
                    run = False
                    self.quit_program()

                # Scan receipt 
                elif selection == "s":

                    select_and_scan_receipt()
                    print(self.get_receipt())

                # Divide receipt 
                elif selection == "d":

                    # set user input parameters
                    correct_input_parameters = ["y", "n", "x"]
                    
                    # Confims that correct receipt has been seleceted
                    correct_receipt = False
                    while not correct_receipt:

                        select_and_scan_receipt()
                        print(self.get_receipt()) 
                        
                        print("Is this the correct receipt? (y/n) or (x) to return to menu.")

                        # creates a while loop to ensure correct input
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

                        # if incorrect receipt was colleted, the user is prombted to select another receipt.
                        if user_input == "n":
                            try:
                                print("Would you like to select another receipt? (y) or (n/x) to return to menu.")
                                user_input = input(">")

                                if user_input not in correct_input_parameters:
                                    raise ValueError("Invalid input. Please enter 'y', 'n' or 'x'.")

                                if user_input == "y":
                                    continue
                                
                                # if the user wished to break the receipt selection loop and return to menu
                                else:
                                    user_input = "x"
                                    break

                            except ValueError as e:
                                print(str(e))

                        # if correct receipt was selected, the user is prombted to select how many shoppers to split the receipt with.
                        if user_input != "x":
                            number_of_shoppers = select_number_of_shoppers()
                            select_shoppers_names(number_of_shoppers)
                        else:
                            pass

                    # prombt to continue to divide receipt
                    total_shopping_cart = True
                    self.create_new_shopper(total_shopping_cart)
                    self.divide_receipt()

    def request_receipt_loaction(self):
        '''Open a file dialog to request the location of a receipt file.'''
        
        root = Tk()
        root.withdraw()  # Hide the main window
        downloads_path = os.path.expanduser("~/Downloads")

        # Open a file dialog to request the location of a receipt file
        path = filedialog.askopenfilename(initialdir=downloads_path, title="Select a file",
                                          filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")))

        return path

    def set_receipt(self, digi_receipt):
        '''Set the digital receipt for further processing.'''
        
        self.__receipt = digi_receipt

    def get_receipt(self):
        '''Get the currently set digital receipt.'''
        
        return self.__receipt

    def get_receipt_file_loaction(self):
        '''Get the receipt file location.'''
        
        return self.__receipt_file_location

    def set_receipt_file_location(self, file_address):
        '''Set the receipt file location.'''
        
        self.__receipt_file_location = file_address

    def get_registered_shoppers(self):
        '''Get the dictionary of registered shoppers.'''
        
        return self.__registered_shoppers

    def set_registered_shoppers(self, shopper_dict):
        '''Set the dictionary of registered shoppers.'''
        
        self.__registered_shoppers = shopper_dict

    def add_registered_shopper(self, shopper):
        '''Add a new shopper to the list of registered shoppers.'''
        
        self.__registered_shoppers[shopper.get_name()] = shopper

    def get_shoppers_in_receipt(self):
        '''Get the dictionary of shoppers in the current receipt.'''
        
        return self.__shoppers_in_receipt

    def add_shopper_to_receipt(self, shopper):
        '''Add a shopper to the list of shoppers in the current receipt.''' 
        
        self.__shoppers_in_receipt[shopper.get_name()] = shopper

    def set_shoppers_dict_in_receipt(self, shopper_dict):
        '''Set the dictionary of shoppers in the current receipt. If "x" passed a paremeter, the dictionary will be reset.'''

        if shopper_dict == "x":
            self.__shoppers_in_receipt = {}
        else:
            self.__shoppers_in_receipt = shopper_dict

    def remove_shopper_from_receipt(self, shopper):
        '''Remove a shopper from the list of shoppers in the current receipt.'''
        
        self.__shoppers_in_receipt.pop(shopper)

    def greeting(self):
        '''Prints a friendly greeting for the user.'''

        # Print a greeting
        print("\nWelcome to the Receipt Divider!")
        print("Designed and Produced by Joshua Scattini.\n")

    def retreive_existing_shoppers(self, file_name="shoppers.txt"):
        '''
        Retrieve and load existing shopper data from a file.

        Parameters:
        - file_name (str): The name of the file containing shopper data.
        '''
        # Check if the file exists
        try:
            with open(file_name, 'r') as file:
                for line in file:
                    shopper_data = line.strip("\n").split(',')
                    
                    # Add the shopper to the list of registered shoppers
                    self.add_registered_shopper(
                        Shopper(str(shopper_data[0]),  # Using the Shopper class, the shopper name is set
                                float(shopper_data[1])))  # Using the Shopper class, the shopper spending tracker is set
        
        # If the file does not exist, create a new file
        except Exception as e:
            self.set_shoppers_dict_to_receipt("x")
            print("CORRUPT_SHOPPER_DATA: The saved shopper was unable to be retrieved.")

    def create_new_shopper(self, receipt_cart=False):
        '''
        Create a new shopper and add them to the list of registered shoppers.

        Parameters:
        - receipt_cart (bool): Flag indicating if the shopper is for the current receipt combined cart.
        '''

        # Check if the shopper is for the current receipt combined cart
        if receipt_cart == False:
            
            # Prompt the user to enter the shopper's name
            valid_input = False
            while not valid_input:
                print("\nPlease enter new shopper's name:\n*'x' to return to menu.*\n")
                user_input = input("<").lower().strip()

                # Check if the shopper already exists
                if user_input in self.get_registered_shoppers():
                    print("Shopper with that name already exists.")

                # Check if the user wishes to return to the menu
                elif user_input == 'x':
                    valid_input = True

                # Create a new shopper
                else:
                    self.add_registered_shopper(Shopper(user_input))
                    print(f"Welcome, {user_input.capitalize()}!")
                    valid_input = True
        
        # If the shopper is for the current receipt combined cart
        else:
            self.add_shopper_to_receipt(Shopper("Combined", None, True, list(self.get_receipt().get_receipt_items().values())))


    def scan_receipt(self, file_location):
        '''
        Scan a receipt file and set the digital receipt for further processing.

        Parameters:
        - file_location (str): The file location of the receipt to be scanned.
        '''

        # Set the file location of the receipt
        scanner = PDFReader()
        scanner.set_file_loaction(file_location)
        
        # Read the file and set the digital receipt
        scanner.read_file()
        scanner.set_digi_receipt()
        digi_receipt = scanner.get_digi_receipt()

        # Assign the generated receipt to the ReceiptDivider object
        self.set_receipt(digi_receipt)

    def divide_receipt(self):
        '''
        Divide the items in the current receipt among the shoppers.

        The function guides the user to assign items to specific shoppers and calculates the amount owed by each shopper.
        '''
        
        # Create a dictionary of shoppers in the current receipt
        def find_current_item_and_cart(while_index):
            
            # Loop through the shoppers in the current receipt
            for shopper_obj in self.get_shoppers_in_receipt().values():
                            for grocery_obj in shopper_obj.get_personal_cart_items():
                                
                                # Check if the item is in the shopper's cart
                                if receipt.get_receipt_items()[while_index] == grocery_obj:
                                    return shopper_obj, grocery_obj

        # Create a dictionary of shoppers in the current receipt
        shopper_dict = {}
        receipt = self.get_receipt()
        receipt_len = len(receipt.get_receipt_items())
        
        # Setting up user input parameters
        user_input_parameters = ["q","w","x","v","e","a","s","d","f","g"]
        
        # Setting up top_str
        top_str = f"\n============================================================"+\
                    f"\n(x) to exit back to menu, (v) submit and calculate owings.\n" +\
                    f"(q) to go to previous item, (w) to go to next item.\n" 
        
        # Setting up shopper_dict
        for i, shopper_obj in enumerate(self.get_shoppers_in_receipt().values(), start=1):
                if shopper_obj.get_name() == "Combined":
                    i = 0

                shopper_dict[user_input_parameters[i+4]] = shopper_obj

        # modifying the user_input_parameters based on number of shoppers
        shopper_str = ""

        # modifyin the user_input_parameters based on number of shoppers
        num_items_to_remove = 5 - (len(shopper_dict)-1)
        user_input_parameters = user_input_parameters[:-num_items_to_remove]

        # Building the shopper_str
        for i, shopper_obj in shopper_dict.items():
            shopper_str += f"({i}) {shopper_obj.get_name().capitalize()}\t"
            print(f"({i}) {shopper_obj.get_name()}")

        print(shopper_str)
        
        while_index = 1
        
        # Loop through the items in the receipt
        submit = False
        while not submit:
            
            # Find the current item and shopper
            item_owner, grocery_item = find_current_item_and_cart(while_index)

            print(top_str)
        
            # Display the current item and shopper
            print(f"Item {while_index} of {receipt_len}")
            print(f"{grocery_item}")

            # Checks to see who's cart the item currently belongs to
            print(f"Currently in {item_owner.get_name().capitalize()}'s cart.")
            print("\nWho will take this item?")
            
            print(shopper_str)
            selection = input(">")
    
            # Checks to see if the user input is valid
            if selection not in user_input_parameters:
                print("Please select of the options below")

            # performs the action based on the user input
            else:
                index_modifier = 1
                
                # Takes the user back to the previous item or next item based on input
                if selection == "q" or selection == "w":
                    if selection == "q":
                        index_modifier *= -1
                    
                    while_index += index_modifier
                    
                    if while_index <= 0:
                        while_index = 1

                    elif while_index >= receipt_len:
                        while_index = receipt_len

                # Takes the user back to the menu or submits the current selections
                elif selection == "x" or selection == "v":
                    if selection == "v":
                        submit = True
                    else: 
                        break
                
                # Adds the item to the selected shoppers cart
                else:
                    
                    item_owner.remove_from_personal_cart(grocery_item)

                    # Add item to selections cart
                    shopper_dict[selection].add_to_personal_cart(receipt.get_receipt_items()[while_index])

                    while_index +=1
                    if while_index > receipt_len:
                        while_index = receipt_len
        
        # Calculate the cart total for each shopper
        for shopper in shopper_dict.values():
            shopper.calculate_cart_total("y")

        # Calculate the amount owed by each shopper
        self.calculate_owings(shopper_dict)                

        # Prombt to confirm and update personal spending tracker
        print("Confirm and update personal spending tracker? (y/n)")
        
        # Loop to ensure correct input
        submit = False
        while not submit:
            
            confirm = input(">")
        
            # if the user wishes to update the spending tracker
            if confirm == "y":
                for shopper in shopper_dict.values():
                    shopper.set_spending_tracker(float('%.2f' % (shopper.get_spending_tracker() + shopper.get_cart_total())))
                submit = True

            # if the user wishes to return to the menu    
            elif confirm == "n":
                break
    
            else:
                print("Please select whether to record change in spending tracker. (y/n)")

    def calculate_owings(self, shopper_dict):
        '''
        Calculate the amount owed by each shopper and display the results.

        Parameters:
        - shopper_dict (dict): A dictionary containing shoppers and their assigned items.
        '''

            ### Split Combined Costs

        # Calculate the split cart and remove the 'Combined' Shopper obj from the dictionary
        split_cart_cost = float('%.2f' % (shopper_dict["e"].get_cart_total() / (len(self.get_shoppers_in_receipt())-1)))
        shopper_dict.pop("e")
        
        # Apply the csplit combined cart toat to each shopper in receipt
        for shopper in shopper_dict.values():
            shopper.set_cart_total(float('%.2f' % (shopper.get_cart_total() + split_cart_cost)))
        
            ### Who Paid 

        # Prombt for who made the payement
        print("Which shoppper made the payment?")

        # Build the string of 'who paid' options to display
        who_paid_str = ""
        for input_sel, shopper in shopper_dict.items():
            who_paid_str += f"({input_sel}) {shopper.get_name().capitalize()}\n"

        # print the built string and capture input
        valid_input = False
        while not valid_input:
            
            print(who_paid_str)
            shopper_paid = input(">")

            # if selection is valid
            if shopper_paid in shopper_dict:
                # Set the selcted Shopper self.__paid to TRUE
                shopper_dict[shopper_paid].set_paid(True)
                valid_input = True
        
            else:
                print("Invalid selection. Please enter the corresponding letter to the shopper who made the payment.")

            ### Build Owing-String
        
        owings_str = ""
        
        # Build 'Shopper x' is owed
        for shopper in shopper_dict.values():
            if shopper.get_paid() == True:
                owings_str += f"{shopper.get_name()} is owed: \n"

        # Build 'amount from "shopper y,z,% etc."'    
        for shopper in shopper_dict.values():
            if shopper.get_paid() == False:
                owings_str += f"${shopper.get_cart_total()} from {shopper.get_name()}.\n"    

        # Display Owing-String
        print(owings_str)

    def show_registered_shoppers(self):
        '''Display the list of registered shoppers.'''
    
        shopper_index = 1

        # Check if there are any registered shoppers and prints message if no shoppers found
        if len(self.get_registered_shoppers()) == 0:
            print("There are no registered shoppers.")

        # Display the list of registered shoppers and their spending tracker
        else:
            print("\nRegistered Shoppers: ")
            for shopper in self.get_registered_shoppers().values():
                print(f"{shopper_index}. {shopper.get_name().capitalize()}\t\tTotal Spent: ${shopper.get_spending_tracker()}")
                shopper_index += 1
            print('')

    def store_shoppers_details(self, file_name="shoppers.txt"):
        '''
        Store the details of registered shoppers in a file.

        Parameters:
        - file_name (str): The name of the file to store shopper details.
        '''
        # Check if there are any registered shoppers
        if len(self.get_registered_shoppers()) != 0:
            with open(file_name, 'w') as file:

                # Loop through the registered shoppers and store their details
                for name, shopper_obj in self.get_registered_shoppers().items():
                    file.write(f'{name},' \
                               f'{shopper_obj.get_spending_tracker()}\n')       

    def run(self):
        '''Run the main program, including greetings, data retrieval, and displaying the menu.'''

        # Opening functions to run upon start-up
        self.greeting()
        self.retreive_existing_shoppers()
        self.display_menu()

    def quit_program(self):
        '''Quit the program and store shopper details before exiting.'''

        # Closing functions to run upon exiting
        self.store_shoppers_details()
        print("Good Bye!")

if __name__ == "__main__":
    # Create an instance of the ReceiptDivider class
    receipt_divider = ReceiptDivider()
    
    # Run the program
    receipt_divider.run()