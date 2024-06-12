# My E-commerce Website  Abyssinia Mobile Shopping

## Aim of the Website

The aim of this website is to provide a seamless and user-friendly e-commerce platform where users can browse and purchase items, manage their profiles, and view their shopping cart. It also includes an admin panel for item management.

## Table of Contents

- [Home Page](#home-page)
- [Login Page](#login-page)
- [Register Page](#register-page)
- [Profile Page](#profile-page)
- [Cart Page](#cart-page)
- [Item Management Page](#item-management-page)

## Home Page

The home page allows users to browse available items. Each item displays its name, price, category, and an image. Users can add items to their cart from here.

![Home Page](static/images/before login.webp)

## Login Page

The login page allows users to log in using their username and password. It includes form validation and error messages for incorrect credentials.

![Login Page](static/images
/before login.webp)

## Register Page

The register page allows new users to create an account by providing a username and password. It includes form validation to ensure all fields are correctly filled.

![Register Page](path/to/registerpage_image.png)

## Profile Page

The profile page displays the logged-in user's information, including their profile image and username. It also provides options to edit the profile and log out.

![Profile Page](path/to/profilepage_image.png)

## Cart Page

The cart page displays the items added to the cart by the user. Each item shows its name, price, category, image, and quantity. The total price is calculated based on the quantity of each item, and a grand total is displayed.

![Cart Page](path/to/cartpage_image.png)

## Item Management Page

The item management page is available to admin users for managing items. Admins can view a list of items with options to edit or delete them. It includes item details such as name, price, category, image, and quantity.

![Item Management Page](path/to/itemmanagement_image.png)

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask, SQLAlchemy, Python
- **Database**: MySQL

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
    ```
2. Navigate to the project directory:
   ```bash
   cd your-repo
   ```
3. Install the dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your database settings in the config.py file.
5. Run the application:
   ```bash
   python app.py
   ```

