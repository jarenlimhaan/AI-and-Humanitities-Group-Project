def create_response(client, From, WHATSAPP_NUMBER, msg) -> None:
    """Create a response message"""
    client.messages.create(
        to=From,
        from_=f'whatsapp:{WHATSAPP_NUMBER}',
        body=msg
    )