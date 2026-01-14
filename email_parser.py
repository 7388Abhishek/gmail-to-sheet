def parse_email(email_data):
    """Return a list suitable for Sheets append"""
    return [
        email_data.get('from', ''),
        email_data.get('subject', ''),
        email_data.get('date', ''),
        email_data.get('body', '')
    ]
