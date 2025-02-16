from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from config import supabase

# Update FastAPI app with metadata
app = FastAPI(
    title="Room Service Agent API",
    description="API for hotel room service management",
    version="1.0.0",
    docs_url="/",  # This will show Swagger UI at root URL
)

# Add basic health check endpoint
@app.get("/health")
async def health_check():
    """Check if the service is running"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Pydantic models
class MenuItem(BaseModel):
    item_id: int
    name: str
    description: Optional[str]
    price: float    
    category: str
    availability: bool = True
    preparation_time: Optional[int] = None
    image_url: Optional[str] = None

class OrderItem(BaseModel):
    item_id: int
    quantity: int
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    booking_id: int
    room_id: int
    special_instructions: Optional[str] = None
    items: List[OrderItem]

# Basic API endpoints
@app.get("/menu", response_model=List[MenuItem])
async def get_menu(category: Optional[str] = None):
    """Get available menu items, optionally filtered by category"""
    query = supabase.table("menu_items").select("*").eq("availability", True)
    
    if category:
        query = query.eq("category", category)
    
    response = query.execute()
    return response.data if response.data else []

@app.post("/orders")
async def create_order(order: OrderCreate):
    """Create a new room service order"""
    # Validate booking exists and is active
    booking = supabase.table("bookings").select("status").eq("booking_id", order.booking_id).execute()
    
    if not booking.data or booking.data[0]["status"] not in ["confirmed", "checked_in"]:
        raise HTTPException(status_code=400, detail="Invalid or inactive booking")

    # Calculate total amount
    total = 0
    items_data = []
    
    for item in order.items:
        menu_item = supabase.table("menu_items").select("price").eq("item_id", item.item_id).execute()
        if not menu_item.data:
            raise HTTPException(status_code=404, detail=f"Menu item {item.item_id} not found")
            
        price = menu_item.data[0]["price"]
        total += price * item.quantity
        items_data.append({
            "item_id": item.item_id,
            "quantity": item.quantity,
            "price": price,
            "notes": item.notes
        })

    # Create order
    order_data = {
        "booking_id": order.booking_id,
        "room_id": order.room_id,
        "special_instructions": order.special_instructions,
        "total_amount": total,
        "status": "pending"
    }

    order_response = supabase.table("room_service_orders").insert(order_data).execute()
    
    if not order_response.data:
        raise HTTPException(status_code=500, detail="Failed to create order")
        
    return {"order_id": order_response.data[0]["order_id"], "status": "pending"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)