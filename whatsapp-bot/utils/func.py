def create_response(client, From, WHATSAPP_NUMBER, msg) -> None:
    """Create a response message"""
    client.messages.create(
        to=From,
        from_=f'whatsapp:{WHATSAPP_NUMBER}',
        body=msg
    )

def create_interactive_response(client, From, WHATSAPP_NUMBER, content_sid) -> None:
    """Create an interactive response message"""
    client.messages.create(
        from_=f'whatsapp:{WHATSAPP_NUMBER}',
        to=From,
        content_sid=content_sid
    )