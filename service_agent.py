from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from config import groq_api_key
from groq_client import GroqClient
from supabase_client import fetch_table_data, update_table_data, insert_table_data

# Define data models for validation
class RoomServiceOrder(BaseModel):
    order_id: int = Field(description="Unique identifier for the room service order")
    booking_id: int = Field(description="Associated booking ID")
    room_id: int = Field(description="Room number for delivery")
    order_time: datetime = Field(description="Time when order was placed")
    delivery_time: Optional[datetime] = Field(description="Time when order was delivered")
    status: str = Field(description="Current status of the order")
    special_instructions: Optional[str] = Field(description="Any special instructions for the order")
    total_amount: float = Field(description="Total cost of the order")

class HousekeepingSchedule(BaseModel):
    schedule_id: int = Field(description="Unique identifier for housekeeping schedule")
    room_id: int = Field(description="Room to be cleaned")
    scheduled_date: datetime = Field(description="Date scheduled for cleaning")
    status: str = Field(description="Current status of housekeeping")
    staff_assigned: Optional[str] = Field(description="Staff member assigned to the task")
    notes: Optional[str] = Field(description="Additional notes about housekeeping")
    completed_at: Optional[datetime] = Field(description="Time when cleaning was completed")

async def get_room_service_orders(status: Optional[str] = None, room_id: Optional[int] = None) -> List[RoomServiceOrder]:
    """Fetch room service orders with optional filtering"""
    orders = fetch_table_data('room_service_orders')
    if status:
        orders = [order for order in orders if order['status'] == status]
    if room_id:
        orders = [order for order in orders if order['room_id'] == room_id]
    return [RoomServiceOrder(**order) for order in orders]

async def update_order_status(order_id: int, new_status: str) -> RoomServiceOrder:
    """Update the status of a room service order"""
    valid_statuses = ['pending', 'preparing', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
    data = {
        'status': new_status,
        'delivery_time': datetime.now().isoformat() if new_status == 'delivered' else None
    }
    updated_order = update_table_data('room_service_orders', order_id, data)
    return RoomServiceOrder(**updated_order[0])

async def get_housekeeping_schedule(date: Optional[datetime] = None, status: Optional[str] = None) -> List[HousekeepingSchedule]:
    """Fetch housekeeping schedule with optional filtering"""
    schedules = fetch_table_data('housekeeping_schedule')
    if date:
        schedules = [schedule for schedule in schedules if schedule['scheduled_date'] == date.isoformat()]
    if status:
        schedules = [schedule for schedule in schedules if schedule['status'] == status]
    return [HousekeepingSchedule(**schedule) for schedule in schedules]

async def update_housekeeping_status(schedule_id: int, new_status: str, notes: Optional[str] = None) -> HousekeepingSchedule:
    """Update the status of a housekeeping schedule"""
    valid_statuses = ['scheduled', 'in_progress', 'completed', 'skipped']
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
    data = {
        'status': new_status,
        'completed_at': datetime.now().isoformat() if new_status == 'completed' else None
    }
    if notes:
        data['notes'] = notes
    updated_schedule = update_table_data('housekeeping_schedule', schedule_id, data)
    return HousekeepingSchedule(**updated_schedule[0])

async def get_room_status_summary() -> Dict:
    """Get a summary of room statuses including pending orders and scheduled cleaning"""
    active_orders = await get_room_service_orders(status='pending')
    today_cleaning = await get_housekeeping_schedule(date=datetime.now())
    return {
        'pending_orders': len(active_orders),
        'scheduled_cleaning': len(today_cleaning),
        'rooms_with_orders': list(set(order.room_id for order in active_orders)),
        'rooms_to_clean': list(set(schedule.room_id for schedule in today_cleaning)),
        'timestamp': datetime.now().isoformat()
    }

# Example usage
async def main():
    try:
        # Fetch and print data from room_service_orders table
        room_service_orders = fetch_table_data('room_service_orders')
        print("Room Service Orders:")
        print(room_service_orders)
        
        # Fetch and print data from housekeeping_schedule table
        housekeeping_schedule = fetch_table_data('housekeeping_schedule')
        print("Housekeeping Schedule:")
        print(housekeeping_schedule)
        
        # Get all pending orders
        result = await get_room_service_orders(status="pending")
        print([order.dict() for order in result])
        
        # Get today's housekeeping schedule
        result = await get_housekeeping_schedule(date=datetime.now())
        print([schedule.dict() for schedule in result])
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())