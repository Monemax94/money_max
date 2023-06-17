# The  MoneyMax

## MoneyMax is an Income and Expenses Tracking Web App

This is a web application for tracking income and expenses. It allows users to manage their financial transactions, categorize income and expenses, and generate reports.

## Technologies Used

- Django: A Python web framework used for the backend development.
- PostgreSQL: An open-source relational database management system used for data storage.
- HTML: Markup language for structuring the web pages.
- JavaScript: Used for client-side interactivity and handling dynamic functionality.
- HTML: Markup language for structuring the web pages.
- CSS: Used for styling and layout of the web pages.

## Features

- User Registration and Authentication: Users can register an account and log in to the app securely.
- Dashboard: Users are provided with a personalized dashboard where they can view their financial summary and recent transactions.
- Income and Expense Management: Users can add, edit, and delete income and expense transactions, along with relevant details such as date, category, and description.
- Categorization: Transactions can be categorized to provide better insights and filtering options.
- Reports: Users can generate reports to get an overview of their income, expenses, and financial trends.
- Search and Filtering: The app provides search functionality and filtering options to help users find specific transactions.
- Responsive Design: The web app is designed to be responsive, providing a seamless experience across different devices and screen sizes.

## Installation

1. Clone the repository: `git clone https://github.com/Monemax94/money_max.git`
2. Navigate to the project directory: `cd your-repo`
3. Set up a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`
6. Set up the PostgreSQL database:
   - Create a new database in PostgreSQL for the project.
   - Update the database configuration in the project's settings.py file.
7. Run database migrations: `python manage.py migrate`
8. Start the development server: `python manage.py runserver`
9. Access the app in your browser at `http://localhost:8000`

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b your-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push the changes to your fork: `git push origin your-branch-name`
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE.txt).

## Acknowledgments

- [ALX Africa](https://www.alxafrica.com/software-engineering/) - Mentorship and training
- [Django](https://www.djangoproject.com/) - The Python web framework used in this project.
- [PostgreSQL](https://www.postgresql.org/) - The open-source relational database management system used for data storage.
- [Bootstrap](https://getbootstrap.com/) - Used for styling the user interface.
- [Chart.js](https://www.chartjs.org/) - Library for creating charts and graphs.
