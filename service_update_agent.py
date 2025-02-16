import sys
from datetime import datetime
from supabase import Client
from config import supabase, groq_api_key
import re

def manage_room_service():
    """Collect room service details and store them in Supabase."""
    print("\n=== Manage Room Service ===")
    room_id = input("Enter Room ID: ")
    service_type = input("Enter Service Type (e.g., 'Dinner'): ")
    status = input("Enter Status (e.g., 'pending', 'preparing'): ")

    try:
        data = {
            "room_id": int(room_id),
            "service_type": service_type,
            "status": status,
            "order_time": datetime.now().isoformat()
        }
        response = supabase.table("room_service_orders").insert(data).execute()
        print("Room Service Order added successfully!")
        print(response.data)
    except Exception as e:
        print(f"Error adding room service order: {e}")

def manage_housekeeping():
    """Collect housekeeping details and store them in Supabase."""
    print("\n=== Manage Housekeeping Schedule ===")
    room_id = input("Enter Room ID: ")
    scheduled_date = input("Enter Scheduled Date (YYYY-MM-DD): ")
    status = input("Enter Status (e.g., 'scheduled'): ")

    try:
        datetime.strptime(scheduled_date, "%Y-%m-%d")
        data = {
            "room_id": int(room_id),
            "scheduled_date": scheduled_date,
            "status": status,
            "created_at": datetime.now().isoformat()
        }
        response = supabase.table("housekeeping_schedule").insert(data).execute()
        print("Housekeeping schedule added successfully!")
        print(response.data)
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
    except Exception as e:
        print(f"Error adding housekeeping schedule: {e}")

def update_housekeeping_to_cleaned(room_id: int):
    """Update the housekeeping status to 'cleaned' for the specified room."""
    data = {"status": "cleaned"}
    response = supabase.table("housekeeping_schedule").update(data).eq("room_id", room_id).execute()
    print("Housekeeping status updated:", response.data)

def process_command(command: str):
    """
    Process natural language commands for hotel service management.
    Examples:
    - "room 101 is cleaned"
    - "mark room 203 as dirty"
    - "order dinner for room 305"
    - "complete room service for 102"
    """
    # Patterns for different commands
    room_cleaned_pattern = r"(?:room\s+)?(\d+)\s+(?:is\s+)?cleaned"
    room_dirty_pattern = r"mark\s+(?:room\s+)?(\d+)\s+(?:as\s+)?dirty"
    room_service_pattern = r"order\s+(\w+)\s+for\s+(?:room\s+)?(\d+)"
    complete_service_pattern = r"complete\s+room\s+service\s+for\s+(?:room\s+)?(\d+)"

    # Check for room cleaning status updates
    if re.search(room_cleaned_pattern, command.lower()):
        room_id = re.search(room_cleaned_pattern, command.lower()).group(1)
        update_housekeeping_status(int(room_id), "cleaned")
        return

    if re.search(room_dirty_pattern, command.lower()):
        room_id = re.search(room_dirty_pattern, command.lower()).group(1)
        update_housekeeping_status(int(room_id), "dirty")
        return

    # Check for room service orders
    if re.search(room_service_pattern, command.lower()):
        match = re.search(room_service_pattern, command.lower())
        service_type = match.group(1)
        room_id = match.group(2)
        create_room_service_order(int(room_id), service_type)
        return

    # Check for completing room service
    if re.search(complete_service_pattern, command.lower()):
        room_id = re.search(complete_service_pattern, command.lower()).group(1)
        complete_room_service(int(room_id))
        return

    print("I don't understand that command. Try something like:")
    print("- room 101 is cleaned")
    print("- mark room 203 as dirty")
    print("- order dinner for room 305")
    print("- complete room service for 102")

def update_housekeeping_status(room_id: int, status: str):
    """Update the housekeeping status for a room."""
    try:
        data = {
            "status": status,
            "scheduled_date": datetime.now().date().isoformat()  # Using scheduled_date instead of last_updated
        }
        response = supabase.table("housekeeping_schedule").update(data).eq("room_id", room_id).execute()
        print(f"Room {room_id} status updated to {status}")
        return response.data
    except Exception as e:
        print(f"Error updating room status: {e}")

def create_room_service_order(room_id: int, service_type: str):
    """Create a new room service order."""
    try:
        data = {
            "room_id": room_id,
            "service_type": service_type,
            "status": "pending",
            "order_time": datetime.now().isoformat()
        }
        response = supabase.table("room_service_orders").insert(data).execute()
        print(f"Room service order ({service_type}) created for room {room_id}")
        return response.data
    except Exception as e:
        print(f"Error creating room service order: {e}")

def complete_room_service(room_id: int):
    """Mark room service as completed."""
    try:
        data = {
            "status": "completed",
            "completion_time": datetime.now().isoformat()
        }
        response = supabase.table("room_service_orders")\
            .update(data)\
            .eq("room_id", room_id)\
            .eq("status", "pending")\
            .execute()
        print(f"Room service completed for room {room_id}")
        return response.data
    except Exception as e:
        print(f"Error completing room service: {e}")

def main():
    """
    Main function to process commands in an interactive way.
    """
    print("=== Hotel Service Agent ===")
    print("You can tell me things like:")
    print("- room 101 is cleaned")
    print("- mark room 203 as dirty")
    print("- order dinner for room 305")
    print("- complete room service for 102")
    print("(Type 'exit' to quit)")
    
    while True:
        command = input("\nWhat would you like me to do? ").strip()
        
        if command.lower() == 'exit':
            break
            
        process_command(command)

if __name__ == "__main__":
    main()