DO $$ BEGIN
    CREATE TYPE app_role AS ENUM (
        'admin',
        'solver'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS app_users (
    user_id VARCHAR(255) PRIMARY KEY,
    role app_role NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

DO $$ BEGIN
    CREATE TYPE ticket_status AS ENUM (
        'open',
        'in_progress',
        'resolved'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status ticket_status NOT NULL DEFAULT 'open',
    created_by VARCHAR(255) NOT NULL,
    assigned_to VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id SERIAL PRIMARY KEY,
    ticket_id INT NOT NULL,
    message_text VARCHAR(1024) NOT NULL,
    author VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT fk_message_ticket
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
);
