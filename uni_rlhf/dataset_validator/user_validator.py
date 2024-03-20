user_schema={
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "type": "object",
    "title": "User Data Schema",
    "required": [
        "username",
        "email",
        "password"
    ],
    "properties": {
        "username": {
            "type": "string",
            "minLength": 3,
            "maxLength": 20,
            "pattern": "^[a-zA-Z0-9_]+$",
            "title": "Username"
        },
        "email": {
            "type": "string",
            "format": "email",
            "title": "Email Address"
        },
        "password": {
            "type": "string",
            "minLength": 3,
            "title": "Password"
        },
    },
    
}
