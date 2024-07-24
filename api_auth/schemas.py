user_create_request_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "username": {"type": "string"},
        "password": {"type": "string"}
        # "is_active": {"type": "boolean"},
        # "is_staff": {"type": "boolean"},
        # "locality": {"type": ["string", "null"]},
        # "facebook": {"type": ["string", "null"], "format": "uri"},
        # "start_date": {"type": ["string", "null"], "format": "date"},
        # "end_date": {"type": ["string", "null"], "format": "date"}
    },
    # "required": ["email", "username", "password", "locality", "facebook", "is_active", "is_staff"]
    "required": ["email", "username", "password"]
}

user_create_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "username": {"type": "string"},
        "is_active": {"type": "boolean"},
        "is_staff": {"type": "boolean"},
        # "locality": {"type": ["string", "null"]},
        # "facebook": {"type": ["string", "null"], "format": "uri"},
        # "start_date": {"type": ["string", "null"], "format": "date"},
        # "end_date": {"type": ["string", "null"], "format": "date"}
    },
    # "required": ["id", "email", "username", "is_active", "is_staff", "locality", "facebook"]
    "required": ["id", "email", "username", "is_active", "is_staff"]
}
