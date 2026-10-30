"""Simple command-line demo of the main project features."""

from datetime import datetime
from zoneinfo import ZoneInfo

from restaurant_app.db import close_pool, get_connection
from restaurant_app.reservations import book_reservation, find_available_tables
from restaurant_app.reviews import add_review


def list_restaurants():
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT id, name, city FROM restaurants ORDER BY name")
        rows = cursor.fetchall()

    print("\nRestaurants")
    for restaurant_id, name, city in rows:
        print(f"  {restaurant_id}. {name} ({city})")


def main():
    zone = ZoneInfo("Africa/Kigali")
    starts_at = datetime(2026, 11, 1, 18, 0, tzinfo=zone)
    ends_at = datetime(2026, 11, 1, 20, 0, tzinfo=zone)

    try:
        while True:
            print("\nRestaurant Reservation System")
            print("1. List restaurants")
            print("2. Find available tables (demo time)")
            print("3. Book a table (demo time)")
            print("4. Add a review")
            print("5. Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                list_restaurants()

            elif choice == "2":
                restaurant_id = int(input("Restaurant ID: "))
                party_size = int(input("Party size: "))
                tables = find_available_tables(
                    restaurant_id, starts_at, ends_at, party_size
                )
                print("Available tables:", tables)

            elif choice == "3":
                restaurant_id = int(input("Restaurant ID: "))
                customer_id = int(
                    input("Customer ID (use 1, 2, or 3 for sample data): ")
                )
                party_size = int(input("Party size: "))
                reservation = book_reservation(
                    restaurant_id, customer_id, starts_at, ends_at, party_size
                )
                print("Reservation confirmed:", reservation)

            elif choice == "4":
                restaurant_id = int(input("Restaurant ID: "))
                customer_id = int(input("Customer ID: "))
                rating = int(input("Rating (1-5): "))
                short_comment = input("Short comment: ")
                detailed_feedback = input("Detailed feedback: ")
                review_id = add_review(
                    restaurant_id, customer_id, rating, short_comment, detailed_feedback
                )
                print(f"Review saved with ID {review_id}.")

            elif choice == "5":
                break
            else:
                print("Please choose an option from 1 to 5.")

    except (ValueError, TypeError) as error:
        print(f"Could not complete request: {error}")
    finally:
        close_pool()


if __name__ == "__main__":
    main()
