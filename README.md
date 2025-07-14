# Event Management System

> A comprehensive event management platform built with Django.

This project provides a robust platform for creating, managing, and promoting events. It allows administrators to organize event details, manage attendee registrations, and track participation. Users can browse upcoming events, register for them, and view their event history.

## Features

*   🗓️ **Event Creation & Management:** Easily create new events with details like date, time, location, and description.
*   🎟️ **User Registration:** Allow users to register for events seamlessly.
*   👨‍👩‍👧‍👦 **Attendee Tracking:** View and manage the list of attendees for each event.
*   🔒 **Secure Authentication:** Built-in user authentication and authorization system.

## Requirements

*   Python 3.8+
*   Django 4.0+
*   pip

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

1.  **Clone the repository**

    ```sh
    git clone https://github.com/subodhchalak/event_management.git
    cd event_management
    ```

2.  **Create a virtual environment and install dependencies**

    It's recommended to use a virtual environment.

    ```sh
    # Create and activate a virtual environment (macOS/Linux)
    python3 -m venv venv
    source venv/bin/activate

    # Create and activate a virtual environment (Windows)
    python -m venv venv
    .\venv\Scripts\activate

    # Install required packages
    pip install -r requirements.txt
    ```

3.  **Apply database migrations**

    ```sh
    python manage.py migrate
    ```

4.  **Create a superuser**

    To access the admin panel, you'll need a superuser account.

    ```sh
    python manage.py createsuperuser
    ```

5.  **Run the development server**

    ```sh
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`.

## Usage

Once the server is running, you can:
*   Access the admin panel at `/admin` to create and manage events.
*   Navigate the main site to view the list of upcoming events.
*   Register as a new user to sign up for events.

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for details on how to contribute to this project. If one doesn't exist, you can explain the process here, for example:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a pull request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.