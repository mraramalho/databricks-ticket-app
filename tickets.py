from fastapi import APIRouter, Request

from auth import (
    get_current_user,
    get_user_role
)

from lakebase import run_query, run_write, run_write_returning


router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"]
)

# View all support tickets
@router.get("")
def list_tickets(request: Request):

    email = get_current_user(request)

    role = get_user_role(email)


    if role in [
        "admin",
        "solver"
    ]:

        sql = """
            SELECT 
                ticket_id,
                title,
                status,
                created_by,
                assigned_to,
                created_at,
                resolved_at
            FROM tickets
            ORDER BY created_at DESC
        """

        return run_query(sql)


    sql = """
        SELECT 
            ticket_id,
            title,
            status,
            created_by,
            assigned_to,
            created_at,
            resolved_at
        FROM tickets
        WHERE created_by = %s
        ORDER BY created_at DESC
    """

    return run_query(
        sql,
        (email,)
    )


# Select a ticket and view its messages
@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, request: Request):
    
    email = get_current_user(request)
    role = get_user_role(email)
    
    # Single query with LEFT JOIN to avoid N+1 problem
    if role in ["admin", "solver"]:
        sql = """
            SELECT 
                t.ticket_id,
                t.title,
                t.status,
                t.created_by,
                t.assigned_to,
                t.created_at as ticket_created_at,
                t.resolved_at,
                m.message_id,
                m.message_text,
                m.author,
                m.created_at as message_created_at
            FROM tickets t
            LEFT JOIN ticket_messages m ON t.ticket_id = m.ticket_id
            WHERE t.ticket_id = %s
            ORDER BY m.created_at ASC
        """
        params = (ticket_id,)
    else:
        sql = """
            SELECT 
                t.ticket_id,
                t.title,
                t.status,
                t.created_by,
                t.assigned_to,
                t.created_at as ticket_created_at,
                t.resolved_at,
                m.message_id,
                m.message_text,
                m.author,
                m.created_at as message_created_at
            FROM tickets t
            LEFT JOIN ticket_messages m ON t.ticket_id = m.ticket_id
            WHERE t.ticket_id = %s AND t.created_by = %s
            ORDER BY m.created_at ASC
        """
        params = (ticket_id, email)
    
    rows = run_query(sql, params)
    
    if not rows:
        return {"error": "Ticket not found or access denied"}
    
    # Extract ticket data (same in all rows)
    first_row = rows[0]
    ticket = {
        "ticket_id": first_row["ticket_id"],
        "title": first_row["title"],
        "status": first_row["status"],
        "created_by": first_row["created_by"],
        "assigned_to": first_row["assigned_to"],
        "created_at": first_row["ticket_created_at"],
        "resolved_at": first_row["resolved_at"]
    }
    
    # Extract messages (one per row, skip if no messages)
    messages = []
    for row in rows:
        if row["message_id"] is not None:
            messages.append({
                "message_id": row["message_id"],
                "message_text": row["message_text"],
                "author": row["author"],
                "created_at": row["message_created_at"]
            })
    
    return {
        "ticket": ticket,
        "messages": messages
    }


# Create a new ticket
@router.post("")
def create_ticket(request: Request, title: str, description: str):
    
    email = get_current_user(request)
    
    sql = """
        INSERT INTO tickets (title, status, created_by)
        VALUES (%s, %s, %s)
        RETURNING ticket_id
    """
    
    result = run_write_returning(
        sql,
        (title, "open", email)
    )
    
    # Create initial message with the description
    if result:
        ticket_id = result[0]["ticket_id"]
        message_sql = """
            INSERT INTO ticket_messages (ticket_id, message_text, author)
            VALUES (%s, %s, %s)
        """
        run_write(message_sql, (ticket_id, description, email))
    
    return {
        "success": True,
        "ticket_id": result[0]["ticket_id"] if result else None,
        "message": "Ticket created successfully"
    }


# Add a message to an existing ticket
@router.post("/{ticket_id}/messages")
def add_message(ticket_id: int, request: Request, message: str):
    
    email = get_current_user(request)
    role = get_user_role(email)
    
    # Verify user has access to this ticket
    if role in ["admin", "solver"]:
        verify_sql = "SELECT ticket_id FROM tickets WHERE ticket_id = %s"
        verify_params = (ticket_id,)
    else:
        verify_sql = "SELECT ticket_id FROM tickets WHERE ticket_id = %s AND created_by = %s"
        verify_params = (ticket_id, email)
    
    ticket_exists = run_query(verify_sql, verify_params)
    
    if not ticket_exists:
        return {"error": "Ticket not found or access denied"}
    
    # Add the message
    sql = """
        INSERT INTO ticket_messages (ticket_id, message_text, author)
        VALUES (%s, %s, %s)
        RETURNING message_id
    """
    
    result = run_write_returning(
        sql,
        (ticket_id, message, email)
    )
    
    return {
        "success": True,
        "message_id": result[0]["message_id"] if result else None,
        "message": "Message added successfully"
    }


# Update a ticket's status
@router.patch("/{ticket_id}/status")
def update_ticket_status(ticket_id: int, request: Request, status: str):
    
    email = get_current_user(request)
    role = get_user_role(email)
    
    # Only admin and solver can update status
    if role not in ["admin", "solver"]:
        return {"error": "Unauthorized: Only admin or solver can update ticket status"}
    
    # Valid statuses
    valid_statuses = ["open", "in_progress", "resolved"]
    
    if status not in valid_statuses:
        return {
            "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }
    
    # Set resolved_at when status becomes 'resolved'
    if status == "resolved":
        sql = """
            UPDATE tickets
            SET status = %s, resolved_at = NOW()
            WHERE ticket_id = %s
            RETURNING ticket_id, status, resolved_at
        """
    else:
        sql = """
            UPDATE tickets
            SET status = %s
            WHERE ticket_id = %s
            RETURNING ticket_id, status
        """
    
    result = run_write_returning(
        sql,
        (status, ticket_id)
    )
    
    if not result:
        return {"error": "Ticket not found"}
    
    return {
        "success": True,
        "ticket_id": result[0]["ticket_id"],
        "new_status": result[0]["status"],
        "message": "Ticket status updated successfully"
    }
