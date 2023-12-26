import fitz

def grab_items_and_price(file_path):

    # Function to extract item description and price from a line
    def find_item_and_price(line, total):
        item = ""
        consecutive_spaces = 0
        
        if not total:
            
            # Extract the item description part of the line
            for char in line:
                
                if char != " ":
                    
                    item += char
                    consecutive_spaces = 0
                
                else:
                    
                    item += " "
                    consecutive_spaces += 1
                    
                    # Break if there are two or more consecutive spaces
                    if consecutive_spaces >= 2:
                        consecutive_spaces = 0
                        break
        else:
            item = "Total"

        if total:
            print(f'item assignened to total: {item}')

        price = ""
        for num in reversed(line.strip()):
            if num != " ": 
                price += str(num)
                consecutive_spaces = 0
            else:
                consecutive_spaces += 1
                # Break if there are two or more consecutive spaces
                
                if consecutive_spaces >= 2:
                    consecutive_spaces = 0
                    # If we're extracting the total, reverse the price string
                    # and strip the '$' character
                    
                    if total or item =="Total":
                        
                        price = price[::-1]
                        return price.strip('$')
                    else:
                        break
        
        price_ready = price[::-1]

        try:
            price_ready = float(price_ready)
        except:
            price_ready = None

        return item, price_ready

    # Load the PDF file
    #file_path = "eReceipt_5799_Mawson20Lakes_18Sep2023__dnakx.pdf"
    doc = fitz.open(file_path)

    items_bought = {}    # Dictionary to store extracted items and their prices
    total_member_dis = 0  # Variable to store the total member discount

    # Iterate through each page of the PDF document
    for page in doc:
        text = page.get_text("text")

        # Split the text into lines
        lines = text.split('\n')

        item_and_price_strings = []  # List to store extracted item description and price
        item_line = ""
        lines_index = 0
        total_found = False

        # Iterate through lines and extract item descriptions and prices
        for line in lines:
            
            if line and line[-1] == " ":
                item_line = line

            if line and (line[1].isdigit() or "Qty" in line[0:10]):
                item_line += line
                line = item_line

            item_and_price_strings.append(line)

            if "  TOTAL" in lines[lines_index] and not total_found:
                total_line = lines[lines_index]
                total_found = True

            if total_found:
                break
            
            lines_index +=1

        # Iterate through extracted lines and parse item descriptions and prices
        for i, line in enumerate(item_and_price_strings):
            qty = 1
            if i < len(item_and_price_strings):
                # Will produce a dictionary of items and price
                item, price = find_item_and_price(line, False)

                if price == None:
                    pass
                elif "Member Price Saving" in item:
                    total_member_dis += price
                else:
                    # Handle cases where the same item appears multiple times
                    if item in items_bought:
                        qty += 1
                        item = (item + f'#{qty}')
                    items_bought[item] = price
        
    total = find_item_and_price(total_line, True)

    # Calculate the total cost of items and compare with the total from the receipt
    '''    item_cost = 0
    
    for item, price in items_bought.items():
        item_cost += price

    item_cost = round(item_cost + total_member_dis, 2)

    if item_cost != total:
        raise ValueError(f"Calculation doesn't match recorded total {total} != {item_cost}")'''
    
    return items_bought, total
