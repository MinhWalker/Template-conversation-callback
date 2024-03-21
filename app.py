import requests
from bottle import Bottle, request

MM_TOKEN = "34844adig7nf7dfmuykni5ob4r"
MM_URL = "https://rnd.chatops.vn"

app = Bottle()

@app.route('/handle-slash-command', method='POST')
def handle_slash_command():
    # Extract the trigger_id from the slash command
    trigger_id = request.forms.get('trigger_id')
    channel_id = request.forms.get('channel_id')

    # Define the dialog
    dialog = {
        "trigger_id": trigger_id,
        "url": "https://81ea-116-101-122-170.ngrok-free.app/submit-form",
        "dialog": {
            "callback_id": "leave-application",
            "title": "Leave Application",
            "elements": [
                {
                    "display_name": "Reason for Leave",
                    "name": "reason",
                    "type": "text",
                    "optional": False
                },
                {
                    "display_name": "Start Date",
                    "name": "start_date",
                    "type": "text",
                    "subtype": "date",
                    "optional": False
                },
                {
                    "display_name": "End Date",
                    "name": "end_date",
                    "type": "text",
                    "subtype": "date",
                    "optional": False
                },
                {
                    "display_name": "Additional Notes",
                    "name": "additional_notes",
                    "type": "textarea",
                    "optional": True
                }
            ],
            "submit_label": "Submit",
            "notify_on_cancel": True,
            "state": channel_id
        }
    }

    # Send a request to Mattermost to open the dialog
    headers = {'Authorization': f'Bearer {MM_TOKEN}'}
    response = requests.post(f'{MM_URL}/api/v4/actions/dialogs/open', json=dialog, headers=headers)

    if response.ok:
        return "Dialog opened successfully."
    else:
        return f"Failed to open dialog: {response.text}"


@app.route('/submit-form', method='POST')
def submit_form():
    # Parse the JSON payload
    data = request.json  # Use request.json to automatically parse the JSON payload
    channel_id = data['state']

    # Extract form fields directly from 'submission'
    reason = data['submission']['reason']
    start_date = data['submission']['start_date']
    end_date = data['submission']['end_date']

    # For optional fields like 'additional_notes', use .get() to avoid KeyError if the field is missing or None
    additional_notes = data['submission'].get('additional_notes', 'None provided')

    # As 'contact_info' wasn't in the provided data structure, it's assumed to be optional or not submitted
    contact_info = data['submission'].get('contact_info', 'Not provided')

    # Construct the leave application message
    leave_application_msg = f"""
    **Leave Application Submitted**
    Reason for Leave: {reason}
    Start Date: {start_date}
    End Date: {end_date}
    Additional Notes: {additional_notes}
    Contact Information: {contact_info}
    """

    # Log the constructed leave application message for debugging

    # Assuming you have a function to post the message to a Mattermost channel
    # channel_id = "gxn7pggkujbgik651x4ha8x7oo"  # Example channel ID
    post_message_to_mattermost(leave_application_msg, channel_id)

    return 'Form submitted successfully'

def post_message_to_mattermost(message, channel_id):
    post_url = f"{MM_URL}/api/v4/posts"
    headers = {
        'Authorization': f'Bearer {MM_TOKEN}',
        'Content-Type': 'application/json',
    }
    post_data = {
        'channel_id': channel_id,
        'message': message
    }
    response = requests.post(post_url, headers=headers, json=post_data)
    if response.status_code == 201:
        print("Message posted successfully")
    else:
        print("Failed to post message")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
