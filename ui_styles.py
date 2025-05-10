# ui_styles.py - CSS styles for the application
def get_css_styles():
    """Return CSS styles for the UI"""
    return """
    <style>
        .full-width-container {
            width: 100%;
            margin: 0;
            padding: 10px;
            background-color: yellow;
            border-radius: 8px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .email-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            padding: 10px;
            border-bottom: 2px solid red;
            background-color: white;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        .email-subject {
            flex: 3;
            color: black;
            font-weight: bold;
        }
        .input-box {
            flex: 2;
            padding: 5px;
        }
        .action-buttons {
            flex: 2;
            display: flex;
            gap: 5px;
            justify-content: center;
        }
        .accept-btn, .edit-btn {
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            text-align: center;
        }
        .accept-btn {
            background-color: red;
            color: white;
        }
        .edit-btn {
            background-color: yellow;
            color: black;
        }
        details {
            width: 100%;
        }
        summary {
            cursor: pointer;
            list-style: none;
            font-size: 16px;
        }
        summary::marker {
            display: none;
        }
        summary::before {
            content: "▶ ";
            font-size: 14px;
            color: red;
        }
        details[open] summary::before {
            content: "▼ ";
            color: red;
        }
        .header-row {
            font-weight: bold; 
            background-color: red; 
            color: white;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .badge-high {
            background-color: #28a745;
            color: white;
        }
        .badge-medium {
            background-color: #ffc107;
            color: black;
        }
        .badge-low {
            background-color: #dc3545;
            color: white;
        }
    </style>
    """