import fitz

def grabItemsAndPrice(file_path):

    # Function to extract item description and price from a line
    def getItemAndPrice(line, total):
        item = ""
        consecutive_spaces = 0

        if not total:
            # Extract the item description part of the line
            for char in line:
                if char != " ":
                    item += char
                    consecutive_spaces = 0
                else:
                    consecutive_spaces += 1
                    # Break if there are two or more consecutive spaces
                    if consecutive_spaces >= 2:
                        consecutive_spaces = 0
                        break

        price = ""
        for num in reversed(line):
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
                    if total:
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

    itemsBought = {}    # Dictionary to store extracted items and their prices
    total_member_dis = 0  # Variable to store the total member discount

    # Iterate through each page of the PDF document
    for page in doc:
        text = page.get_text("text")

        # Split the text into lines
        lines = text.split('\n')

        itemAndPriceStrings = []  # List to store extracted item description and price
        itemLine = ""

        # Iterate through lines and extract item descriptions and prices
        for line in lines:
            if line and line[-1] == " ":
                itemLine = line

            if line and (line[1].isdigit() or line.startswith(" Qty")):
                itemLine += line
                line = itemLine

            itemAndPriceStrings.append(line)

        # Iterate through extracted lines and parse item descriptions and prices
        for i, line in enumerate(itemAndPriceStrings):
            qty = 1
            if i < len(itemAndPriceStrings) - 29:
                # Will produce a dictionary of items and price
                item, price = getItemAndPrice(line, False)

                if price == None:
                    pass
                elif item == "MemberPriceSaving":
                    total_member_dis += price
                else:
                    # Handle cases where the same item appears multiple times
                    if item in itemsBought:
                        qty += 1
                        item = (item + f'#{qty}')
                    itemsBought[item] = price
        
        # Extract the total line
        total_line = itemAndPriceStrings[-27]
        total = getItemAndPrice(total_line, True)

    # Calculate the total cost of items and compare with the total from the receipt
    item_cost = 0
    #print("Total number of items:", len(itemsBought))
    for item, price in itemsBought.items():
        #print(f'{item} : ${price}')
        item_cost += price

    item_cost = item_cost + total_member_dis
    item_cost = round(item_cost, 2)

    return itemsBought, total
