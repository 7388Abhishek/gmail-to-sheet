from gmail_service import get_gmail_service

if __name__ == "__main__":
    service = get_gmail_service()
    print("✅ Gmail API Authenticated Successfully")
from gmail_service import authenticate_gmail, get_unread_emails, fetch_email, mark_as_read, load_state, save_state
from sheets_service import authenticate_sheets, append_row
from email_parser import parse_email

def main():
    gmail_service = authenticate_gmail()
    sheet_service = authenticate_sheets()
    state = load_state()
    processed_ids = set(state.get("processed_ids", []))

    messages = get_unread_emails(gmail_service)
    if not messages:
        print("No new emails found.")
        return

    for msg in messages:
        msg_id = msg['id']
        if msg_id in processed_ids:
            continue
        email_data = fetch_email(gmail_service, msg_id)
        row = parse_email(email_data)
        append_row(sheet_service, row)
        mark_as_read(gmail_service, msg_id)
        processed_ids.add(msg_id)
        print(f"Processed email: {email_data.get('subject', '')}")

    save_state({"processed_ids": list(processed_ids)})
    print("All new emails processed and saved to Google Sheet.")

if __name__ == "__main__":
    main()
