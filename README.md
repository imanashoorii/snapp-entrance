# Snappfood Simple Orders Management

## Overview

This Django app serves as a simple and a basic concept of Snappfood delivery system. Users can track their order and report delay about their order. In addition, Snapp operators can assign themselves to these reports and manage them. Also, They can see the weekly report of the vendors delays.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/imanashoorii/snapp-entrance.git
   cd snapp-entrance
   ```
2. Install dependencies using pip and the provided requirements.txt:
    ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations to set up the database:
   ```bash
   python manage.py migrate
   ```
   
## Docker Installation

Just run ```docker compose up -d --build``` and easily you can use with the server ip and 80 port.
## Usage
### Running the Development Server
Start the development server:
   ```bash
   python manage.py runserver
   ```
Visit http://127.0.0.1:8000/ in your web browser to access the app.

### User Registration and Login
There is no need for user authentication in this level.

### Report Delay
To report a delay, send a GET request with the "order_id" which is the pk of the order.

   ```bash
      curl 127.0.0.1:8000/api/delay/report/{order_id}/
   ```

Example using `curl`:

   ```bash
      curl 127.0.0.1:8000/api/delay/report/2/
   ```
### Assign Operator to a delay
To assign a delay to operator, send a POST request with "employee" parameter in the body as json which is equals to operator id. Note that it should be set from requested user but for now as there is no authentication system and user management, we set it manually in the body of the request.

   ```bash
      curl -X POST -H "Content-Type: application/json" -d '{"employee": employee_id}' 127.0.0.1:8000/api/delay/assign
   ```
### Retrieve Vendor Delays Weekly Report
To list all the weekly delays of a vendor, send a GET request to this view and see the list of each vendor and its delays.

   ```bash
      curl 127.0.0.1:8000/api/delay/report/weekly
   ```

### API Endpoints
* `delay/report/<int:order_id>/`: Report a delay about an order using a GET request as described above.
* `delay/report/weekly`: List weekly delays of a vendor using a GET request as described above.
* `delay/assign`: Assign operator to a delay using a POST request as described above.

### Tests
You can easily run written tests by the below command. 
   ```bash
      python manage.py test api.tests
   ```
### Contact
For any inquiries, please contact me at [imanashoorii.77@gmail.com](imanashoorii.77@gmail.com) .

