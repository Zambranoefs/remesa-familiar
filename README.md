# remesa-familiar (Family remittance)

I created my project in Spanish because I intend to use it for professional purposes.

This project is a web application.

People can register on the website, and to do so they must provide some information that will be stored in a database called remesa_familiar.db

*** MAIN FUNCTIONS ***

- After the registration, the user (from now on "customer") is automatically redirected to the index (Tab "Iniciar pedido").
In there, customers can check the rate of the date and then create a remittance order, by specifying the amount of euros they want to send to their
friends of family members (the conversion is made automatically). The bank account must be specified too.

- Once the customer clicks on "Iniciar pedido" (Create order), the customer is redirected to the confirmation page, where customers can verify that all
the information related to the remittance they created, is correct. In case it isn't, they can click on "Cancelar" (Cancel) to return to the
index, to create a new order from scratch. In case the customers consider that everything is correct, they can click on "Confirmar" (Confirm).

- The customer is then redirected to the history page (Tab "Mi historial de pedidos"), where a green prompt appears, stating that the order has been registered.
On this page, customers can check all the orders they have made. They can also delete any of those orders, after selecting its corresponding number, not before
being alerted about this action.

*** MANAGEMENT FUNCTIONS ***

* BANK ACCOUNTS * (Tab "Mis cuentas bancarias")

- Customers may:
    - Add new bank accounts.
    - Delete existing ones.

* PROFILE * (Tab "Mi perfil")

- Customers may:
    - Update their password.
    - Delete their account, not before being alerted about this action.

*** OTHER FUNCTIONS ***

* LOG OUT *

- Customers may log out by clicking on "Cerrar sesión".

* PASSWORD FORGOTTEN *

- Customers who have forgotten their password may create a new one by clicking on "Recupérala aquí" (Recover it here) on the login page.

- After clicking on that button, customers are redirected to the recover page, where they must provide their id number and the correct answers
to the two security questions they answered during the registration.

- If all the answers are correct, customers are redirected to the new_password page, where they can create a new password.
