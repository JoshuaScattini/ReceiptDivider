# Receipt Splitter

This project consists of a PDF reader and item cost extraction script along with a graphical user interface (GUI) for splitting online PDF receipts among multiple shoppers.

### PDF Reader and Item Cost Extraction (File 1)

## Requirements
- Python 3
- PyMuPDF (`fitz`)

## Usage

```
# Example usage of the PDF reader script
import RecieptReader

# Replace 'your_file_path.pdf' with the actual path to your receipt PDF collected by the GUI
file_path = "example.pdf"
items, total = RecieptReader.grabItemsAndPrice(file_path)

# Access the extracted items and their prices
print("Extracted Items:")
for item, price in items.items():
    print(f"{item}: ${price:.2f}")

# Access the total amount from the receipt
print("Total Amount: ${:.2f}".format(total))
```

---

### GUI (File 2)

## Requirements

Python 3
CustomTkinter

##Usage

```
# Example usage of the GUI
import customtkinter
from customtkinter import *
import RecieptReader
from RecieptReader import *

# Set up the appearance mode and default color theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
```

# Run the GUI
python GUI_script.py

## Features
- The GUI allows users to load online receipt PDFs.
- It provides a user-friendly interface for categorizing items among shoppers.
- Users can calculate and view the total expenses for each shopper.
Contributing

## Contributing

Contributions from the community are currently not being accepted. This project is a solo project currently developed and maintained by Joshua Scattini, and external contributions are not being considered at this time. 
If you have suggestions, bug reports, or feature requests, feel free to [open an issue](https://github.com/yourusername/yourproject/issues), and they will be considered by the project maintainer.

License
This project is licensed under the MIT License.

## Image Attribution

The images used in this project are sourced from [Icons8](https://icons8.com). Below are the attributions for each image:

- User Group image: [User Groups](https://icons8.com/icon/9542/user-groups)
- Receipt Image: [Receipt](https://icons8.com/icon/CRW8QYTd3kse/cash-receipt)

## Contact Information

Feel free to reach out if you have any questions, suggestions, or other collaboration opportunities:

- **Email:** [JoshuaScattini93@gmail.com](mailto:JoshuaScattini93@gmail.com)
- **LinkedIn:** [Joshua Scattini](https://www.linkedin.com/in/joshua-scattini/)
