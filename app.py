import streamlit as st
from datetime import date


# ============================================================
# BOOK CLASS
# ============================================================

class Book:
    def __init__(self, isbn, title, author, publication_year, status="Available"):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.status = status

    def reserve_book(self):
        if self.status == "Available":
            self.status = "Reserved"
            return "Book reserved successfully."

        return "Book is not available for reservation."

    def update_status(self, new_status):
        valid_statuses = ["Available", "Reserved", "Checked Out"]

        if new_status in valid_statuses:
            self.status = new_status
            return "Status updated successfully."

        return "Invalid status."


# ============================================================
# PATRON CLASS
# ============================================================

class Patron:
    def __init__(
        self,
        patron_id,
        name,
        email,
        borrowed_books=None,
        fine_balance=0
    ):
        self.patron_id = patron_id
        self.name = name
        self.email = email
        self.borrowed_books = borrowed_books or []
        self.fine_balance = fine_balance

    def view_borrowed_books(self):
        return self.borrowed_books

    def pay_fine(self, amount):

        if amount <= 0:
            return "Payment must be greater than 0."

        if self.fine_balance == 0:
            return "You do not have any outstanding fines."

        if amount >= self.fine_balance:
            change = amount - self.fine_balance
            self.fine_balance = 0

            if change > 0:
                return f"Fine paid successfully. Change: ₹{change}"

            return "Fine paid successfully."

        # Partial payment
        self.fine_balance -= amount

        return (
            f"Payment successful. "
            f"Remaining fine: ₹{self.fine_balance}"
        )


# ============================================================
# LIBRARY SYSTEM CLASS
# ============================================================

class LibrarySystem:

    def __init__(
        self,
        book_inventory=None,
        patron_registry=None,
        max_borrow_limit=3,
        daily_fine_rate=5
    ):
        self.book_inventory = book_inventory or {}
        self.patron_registry = patron_registry or {}
        self.max_borrow_limit = max_borrow_limit
        self.daily_fine_rate = daily_fine_rate

    # --------------------------------------------------------
    # ADD BOOK
    # --------------------------------------------------------

    def add_book(self, book_object):

        if book_object.isbn in self.book_inventory:
            return "A book with this ISBN already exists."

        self.book_inventory[book_object.isbn] = book_object

        return "Book added successfully."

    # --------------------------------------------------------
    # VIEW BOOKS
    # --------------------------------------------------------

    def view_all_books(self):
        return list(self.book_inventory.values())

    # --------------------------------------------------------
    # REGISTER PATRON
    # --------------------------------------------------------

    def register_patron(self, patron_object):

        if patron_object.patron_id in self.patron_registry:
            return "Patron already exists."

        self.patron_registry[patron_object.patron_id] = patron_object

        return "Patron registered successfully."

    # --------------------------------------------------------
    # SEARCH BOOK
    # --------------------------------------------------------

    def search_books(self, query):

        results = []

        for book in self.book_inventory.values():

            if query.lower() in book.title.lower():

                results.append(book)

        return results

    # --------------------------------------------------------
    # CHECK OUT BOOK
    # --------------------------------------------------------

    def check_out_book(self, patron_id, isbn):

        if patron_id not in self.patron_registry:
            return "Patron not found."

        if isbn not in self.book_inventory:
            return "Book not found."

        patron = self.patron_registry[patron_id]
        book = self.book_inventory[isbn]

        if book.status != "Available":
            return "Book is not available."

        if len(patron.borrowed_books) >= self.max_borrow_limit:
            return "Borrowing limit reached."

        if patron.fine_balance > 100:
            return "Outstanding fine is too high."

        patron.borrowed_books.append(book)

        book.update_status("Checked Out")

        return "Book checked out successfully."

    # --------------------------------------------------------
    # RETURN BOOK
    # --------------------------------------------------------

    def return_book(self, patron_id, isbn):

        if patron_id not in self.patron_registry:
            return "Patron not found."

        if isbn not in self.book_inventory:
            return "Book not found."

        patron = self.patron_registry[patron_id]
        book = self.book_inventory[isbn]

        if book in patron.borrowed_books:

            patron.borrowed_books.remove(book)

            book.update_status("Available")

            return "Book returned successfully."

        return "This book was not borrowed by the patron."

    # --------------------------------------------------------
    # CALCULATE FINE
    # --------------------------------------------------------

    def calculate_overdue_fine(self, due_date):

        current_date = date.today()

        if current_date > due_date:

            overdue_days = (
                current_date - due_date
            ).days

            return overdue_days * self.daily_fine_rate

        return 0


# ============================================================
# LIBRARIAN CLASS
# ============================================================

class Librarian:

    def __init__(
        self,
        user_id,
        name,
        employee_id,
        access_level,
        library
    ):
        self.user_id = user_id
        self.name = name
        self.employee_id = employee_id
        self.access_level = access_level
        self.library = library

    # --------------------------------------------------------
    # REMOVE BOOK
    # --------------------------------------------------------

    def remove_book(self, isbn):

        if isbn not in self.library.book_inventory:
            return "Book not found."

        book = self.library.book_inventory[isbn]

        if book.status == "Checked Out":
            return "Cannot remove a checked-out book."

        del self.library.book_inventory[isbn]

        return "Book removed successfully."

    # --------------------------------------------------------
    # WAIVE FINE
    # --------------------------------------------------------

    def waive_fine(self, patron_id, amount):

        if patron_id not in self.library.patron_registry:
            return "Patron not found."

        if amount <= 0:
            return "Waiver amount must be greater than 0."

        patron = self.library.patron_registry[patron_id]

        patron.fine_balance -= amount

        if patron.fine_balance < 0:
            patron.fine_balance = 0

        return "Fine waived successfully."


# ============================================================
# STREAMLIT SESSION STATE
# ============================================================

if "library" not in st.session_state:

    st.session_state.library = LibrarySystem(
        max_borrow_limit=3,
        daily_fine_rate=5
    )

    # Sample books
    sample_books = [
        Book(
            "101",
            "Python Programming",
            "Mark Lutz",
            2021
        ),
        Book(
            "102",
            "Data Science Handbook",
            "Jake VanderPlas",
            2020
        ),
        Book(
            "103",
            "Machine Learning",
            "Tom Mitchell",
            2019
        )
    ]

    for book in sample_books:
        st.session_state.library.add_book(book)

    # Sample patron
    patron = Patron(
        "P001",
        "Vikrant",
        "vikrant@example.com"
    )

    st.session_state.library.register_patron(patron)


# Create librarian
if "librarian" not in st.session_state:

    st.session_state.librarian = Librarian(
        user_id="U001",
        name="Admin",
        employee_id="EMP001",
        access_level="Admin",
        library=st.session_state.library
    )


library = st.session_state.library
librarian = st.session_state.librarian


# ============================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📚 Library Management System")

st.write(
    "A simple Library Management System built using "
    "Python OOP and Streamlit."
)


# ============================================================
# SIDEBAR MENU
# ============================================================

st.sidebar.title("Navigation")

menu = st.sidebar.radio(
    "Select Operation",
    [
        "Dashboard",
        "View All Books",
        "Add Book",
        "Search Books",
        "Register Patron",
        "Check Out Book",
        "Return Book",
        "Reserve Book",
        "Patron Details",
        "Pay Fine",
        "Librarian",
        "Remove Book",
        "Waive Fine"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if menu == "Dashboard":

    st.header("📊 Dashboard")

    total_books = len(library.book_inventory)

    available_books = sum(
        1
        for book in library.book_inventory.values()
        if book.status == "Available"
    )

    reserved_books = sum(
        1
        for book in library.book_inventory.values()
        if book.status == "Reserved"
    )

    checked_out_books = sum(
        1
        for book in library.book_inventory.values()
        if book.status == "Checked Out"
    )

    total_patrons = len(library.patron_registry)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Books", total_books)
    col2.metric("Available", available_books)
    col3.metric("Reserved", reserved_books)
    col4.metric("Checked Out", checked_out_books)
    col5.metric("Patrons", total_patrons)


# ============================================================
# VIEW ALL BOOKS
# ============================================================

elif menu == "View All Books":

    st.header("📚 All Books")

    books = library.view_all_books()

    if not books:

        st.info("No books available.")

    else:

        book_data = []

        for book in books:

            book_data.append({
                "ISBN": book.isbn,
                "Title": book.title,
                "Author": book.author,
                "Publication Year": book.publication_year,
                "Status": book.status
            })

        st.dataframe(
            book_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ADD BOOK
# ============================================================

elif menu == "Add Book":

    st.header("➕ Add New Book")

    isbn = st.text_input("ISBN")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    publication_year = st.number_input(
        "Publication Year",
        min_value=1000,
        max_value=2100,
        value=2025
    )

    if st.button("Add Book"):

        if not isbn or not title or not author:

            st.warning("Please fill all fields.")

        else:

            book = Book(
                isbn,
                title,
                author,
                publication_year
            )

            result = library.add_book(book)

            if "successfully" in result:
                st.success(result)
            else:
                st.error(result)


# ============================================================
# SEARCH BOOKS
# ============================================================

elif menu == "Search Books":

    st.header("🔎 Search Books")

    query = st.text_input(
        "Enter book title"
    )

    if query:

        results = library.search_books(query)

        if not results:

            st.warning("No books found.")

        else:

            for book in results:

                st.write(
                    f"**{book.title}** | "
                    f"ISBN: {book.isbn} | "
                    f"Author: {book.author} | "
                    f"Status: {book.status}"
                )


# ============================================================
# REGISTER PATRON
# ============================================================

elif menu == "Register Patron":

    st.header("👤 Register Patron")

    patron_id = st.text_input("Patron ID")
    name = st.text_input("Name")
    email = st.text_input("Email")

    if st.button("Register Patron"):

        if not patron_id or not name or not email:

            st.warning("Please fill all fields.")

        else:

            patron = Patron(
                patron_id,
                name,
                email
            )

            result = library.register_patron(patron)

            if "successfully" in result:
                st.success(result)
            else:
                st.error(result)


# ============================================================
# CHECK OUT BOOK
# ============================================================

elif menu == "Check Out Book":

    st.header("📖 Check Out Book")

    if not library.patron_registry:

        st.warning("No patrons registered.")

    else:

        patron_id = st.selectbox(
            "Select Patron",
            list(library.patron_registry.keys())
        )

        available_books = [
            book
            for book in library.book_inventory.values()
            if book.status == "Available"
        ]

        if not available_books:

            st.warning("No books available for checkout.")

        else:

            isbn = st.selectbox(
                "Select Book",
                [
                    f"{book.isbn} - {book.title}"
                    for book in available_books
                ]
            )

            selected_isbn = isbn.split(" - ")[0]

            if st.button("Check Out"):

                result = library.check_out_book(
                    patron_id,
                    selected_isbn
                )

                if "successfully" in result:
                    st.success(result)
                else:
                    st.error(result)


# ============================================================
# RETURN BOOK
# ============================================================

elif menu == "Return Book":

    st.header("↩️ Return Book")

    patron_ids = list(
        library.patron_registry.keys()
    )

    if not patron_ids:

        st.warning("No patrons available.")

    else:

        patron_id = st.selectbox(
            "Select Patron",
            patron_ids
        )

        patron = library.patron_registry[patron_id]

        if not patron.borrowed_books:

            st.info("This patron has no borrowed books.")

        else:

            selected_book = st.selectbox(
                "Select Book",
                [
                    f"{book.isbn} - {book.title}"
                    for book in patron.borrowed_books
                ]
            )

            selected_isbn = selected_book.split(" - ")[0]

            if st.button("Return Book"):

                result = library.return_book(
                    patron_id,
                    selected_isbn
                )

                if "successfully" in result:
                    st.success(result)
                else:
                    st.error(result)


# ============================================================
# RESERVE BOOK
# ============================================================

elif menu == "Reserve Book":

    st.header("🔖 Reserve Book")

    available_books = [
        book
        for book in library.book_inventory.values()
        if book.status == "Available"
    ]

    if not available_books:

        st.info("No available books.")

    else:

        selected_book = st.selectbox(
            "Select Book",
            [
                f"{book.isbn} - {book.title}"
                for book in available_books
            ]
        )

        selected_isbn = selected_book.split(" - ")[0]

        if st.button("Reserve Book"):

            book = library.book_inventory[selected_isbn]

            result = book.reserve_book()

            if "successfully" in result:
                st.success(result)
            else:
                st.error(result)


# ============================================================
# PATRON DETAILS
# ============================================================

elif menu == "Patron Details":

    st.header("👤 Patron Details")

    patron_ids = list(
        library.patron_registry.keys()
    )

    if not patron_ids:

        st.info("No patrons registered.")

    else:

        patron_id = st.selectbox(
            "Select Patron",
            patron_ids
        )

        patron = library.patron_registry[patron_id]

        st.subheader(patron.name)

        col1, col2, col3 = st.columns(3)

        col1.write(f"**Patron ID:** {patron.patron_id}")
        col2.write(f"**Email:** {patron.email}")
        col3.write(f"**Fine:** ₹{patron.fine_balance}")

        st.subheader("Borrowed Books")

        if not patron.borrowed_books:

            st.info("No books borrowed.")

        else:

            data = []

            for book in patron.borrowed_books:

                data.append({
                    "ISBN": book.isbn,
                    "Title": book.title,
                    "Author": book.author
                })

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# PAY FINE
# ============================================================

elif menu == "Pay Fine":

    st.header("💰 Pay Fine")

    patron_ids = list(
        library.patron_registry.keys()
    )

    patron_id = st.selectbox(
        "Select Patron",
        patron_ids
    )

    patron = library.patron_registry[patron_id]

    st.write(
        f"Outstanding Fine: **₹{patron.fine_balance}**"
    )

    amount = st.number_input(
        "Payment Amount",
        min_value=0.0,
        step=10.0
    )

    if st.button("Pay Fine"):

        result = patron.pay_fine(amount)

        if "successfully" in result or "Payment successful" in result:
            st.success(result)
        else:
            st.error(result)


# ============================================================
# LIBRARIAN DETAILS
# ============================================================

elif menu == "Librarian":

    st.header("👨‍💼 Librarian")

    st.write(
        f"**Name:** {librarian.name}"
    )

    st.write(
        f"**Employee ID:** {librarian.employee_id}"
    )

    st.write(
        f"**Access Level:** {librarian.access_level}"
    )


# ============================================================
# REMOVE BOOK
# ============================================================

elif menu == "Remove Book":

    st.header("🗑️ Remove Book")

    books = list(
        library.book_inventory.values()
    )

    if not books:

        st.info("No books available.")

    else:

        selected_book = st.selectbox(
            "Select Book",
            [
                f"{book.isbn} - {book.title}"
                for book in books
            ]
        )

        selected_isbn = selected_book.split(" - ")[0]

        if st.button("Remove Book"):

            result = librarian.remove_book(
                selected_isbn
            )

            if "successfully" in result:
                st.success(result)
            else:
                st.error(result)


# ============================================================
# WAIVE FINE
# ============================================================

elif menu == "Waive Fine":

    st.header("⚖️ Waive Fine")

    patron_ids = list(
        library.patron_registry.keys()
    )

    if not patron_ids:

        st.info("No patrons registered.")

    else:

        patron_id = st.selectbox(
            "Select Patron",
            patron_ids
        )

        patron = library.patron_registry[patron_id]

        st.write(
            f"Current Fine: **₹{patron.fine_balance}**"
        )

        amount = st.number_input(
            "Waiver Amount",
            min_value=0.0,
            step=10.0
        )

        if st.button("Waive Fine"):

            result = librarian.waive_fine(
                patron_id,
                amount
            )

            if "successfully" in result:
                st.success(result)
            else:
                st.error(result)