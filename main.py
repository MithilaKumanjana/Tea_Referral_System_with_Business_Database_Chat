import gradio as gr
from database_system import TeaBusinessDatabase, ReferralSystem
# from chat_system import DatabaseChatBot
from chat_syetem_with_chat_gpt import DatabaseChatBot

def create_application():
    """Create the complete application with two main sections"""
    
    # Initialize system components
    print("Initializing Tea Business System...")
    database = TeaBusinessDatabase()
    referral_system = ReferralSystem(database)
    chatbot = DatabaseChatBot(referral_system)
    print("System initialization complete!")
    
    with gr.Blocks(
        title="Tea Business Management System",
        theme=gr.themes.Soft()
    ) as demo:
        
        gr.Markdown("""
        # Tea Business Management System
        **Complete customer registration and referral tracking with AI chat**
        """)
        
        with gr.Tabs():
            
            # SECTION 1: DATABASE MANAGEMENT INTERFACE
            with gr.TabItem("Database Management"):
                gr.Markdown("### Customer Registration and Data Management")
                
                with gr.Row():
                    # Customer Registration
                    with gr.Column():
                        gr.Markdown("#### Register New Customer")
                        
                        name_input = gr.Textbox(
                            label="Customer Name",
                            placeholder="Enter full name (e.g., John Doe)"
                        )
                        
                        phone_input = gr.Textbox(
                            label="Phone Number",
                            placeholder="Enter phone number (e.g., 0771234567)"
                        )
                        
                        referral_input = gr.Textbox(
                            label="Referral Code (Optional)",
                            placeholder="Enter referral code if customer was referred"
                        )
                        
                        with gr.Row():
                            register_btn = gr.Button("Register Customer", variant="primary")
                            clear_btn = gr.Button("Clear", variant="secondary")
                    
                    # Registration Results
                    with gr.Column():
                        registration_output = gr.Textbox(
                            label="Registration Results",
                            lines=15,
                            interactive=False
                        )
                
                # Customer Lookup Section
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Customer Lookup")
                        
                        search_input = gr.Textbox(
                            label="Search Customer",
                            placeholder="Enter name, ID, or phone number"
                        )
                        
                        lookup_btn = gr.Button("Find Customer", variant="primary")
                    
                    with gr.Column():
                        lookup_output = gr.Textbox(
                            label="Customer Information",
                            lines=15,
                            interactive=False
                        )
                
                # Code Validation Section
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Referral Code Validation")
                        
                        code_input = gr.Textbox(
                            label="Referral Code",
                            placeholder="Enter referral code to validate"
                        )
                        
                        validate_btn = gr.Button("Validate Code", variant="primary")
                    
                    with gr.Column():
                        validation_output = gr.Textbox(
                            label="Validation Results",
                            lines=8,
                            interactive=False
                        )
            
            # SECTION 2: CHATBOT INTERFACE
            with gr.TabItem("Chat with Database"):
                gr.Markdown("### Ask Questions About Your Business Data")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        chat_interface = gr.Chatbot(
                            value=[("System", "Hello! I can answer questions about your tea business data. Ask me anything!")],
                            height=500,
                            label="Business Data Assistant"
                        )
                        
                        with gr.Row():
                            chat_input = gr.Textbox(
                                placeholder="Ask about your customers, referrals, or statistics...",
                                scale=4,
                                show_label=False
                            )
                            send_btn = gr.Button("Send", scale=1, variant="primary")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Quick Questions:")
                        
                        quick_questions = [
                            "How many customers do I have?",
                            "Who are my top referrers?",
                            "Show customers with discounts",
                            "What's my referral success rate?",
                            "Who registered recently?",
                            "Show me referral code usage",
                            "Find customer named John",
                            "Show me general statistics"
                        ]
                        
                        for question in quick_questions:
                            quick_btn = gr.Button(question, variant="secondary", size="sm")
                            quick_btn.click(
                                lambda q=question: q,
                                outputs=[chat_input]
                            )
        
        # Database Management Functions
        def register_customer_interface(name, phone, referral_code):
            """Handle customer registration"""
        def register_customer_interface(name, phone, referral_code):
            """Handle customer registration"""
            if not name.strip() or not phone.strip():
                return "Please enter both customer name and phone number."
            
            result = referral_system.register_customer(name, phone, referral_code if referral_code.strip() else None)
            
            if result["success"]:
                response = f"""Customer Registration Successful!

Customer Details:
- Name: {result['customer_data']['name']}
- Phone: {result['customer_data']['phone']}
- Customer ID: {result['customer_id']}
- Registration Date: {result['customer_data']['registration_date'][:10]}

Generated Referral Codes:
1. {result['referral_codes'][0]}
2. {result['referral_codes'][1]}
3. {result['referral_codes'][2]}

Instructions:
- Give these 3 referral codes to the customer
- Customer shares codes with friends and family
- When 3 people use the codes, customer earns discount

Current Status:
- Referrals Completed: 0/3
- Discount Earned: No
- Account Status: Active"""
                
                if referral_code and referral_code.strip():
                    response += f"\n\nReferral Information:\n• Customer was referred using code: {referral_code.upper()}"
                
                return response
            else:
                return f"Registration Failed: {result['message']}"
        
        def lookup_customer_interface(search_term):
            """Handle customer lookup"""
            if not search_term.strip():
                return "Please enter a search term (name, ID, or phone number)."
            
            result = referral_system.get_customer_info(search_term)
            
            if result["found"]:
                customer = result["customer"]
                referral_details = result["referral_details"]
                
                response = f"""Customer Information Found:

Basic Details:
- Customer ID: {customer['customer_id']}
- Name: {customer['name']}
- Phone: {customer['phone']}
- Registration Date: {customer['registration_date'][:10]}
- Referred By: {customer['referred_by']}

Referral Progress:
- Completed Referrals: {customer['referrals_completed']}/3
- Discount Status: {customer['discount_earned']}
- Account Status: {customer['status']}

Referral Codes Status:"""
                
                for detail in referral_details:
                    response += f"\n• {detail['code']} - {detail['status']}"
                    if detail['status'] == 'Used':
                        response += f" (Used by {detail['used_by_name']} on {detail['date_used']})"
                
                if customer['discount_earned'] == 'Yes':
                    response += f"\n\nCONGRATULATIONS! This customer has earned a discount!"
                elif customer['referrals_completed'] == 2:
                    response += f"\n\nAlmost there! Just 1 more referral needed for discount."
                elif customer['referrals_completed'] == 1:
                    response += f"\n\nGood progress! 2 more referrals needed for discount."
                else:
                    response += f"\n\nEncourage customer to share referral codes with friends."
                
                return response
            else:
                return result["message"]
        
        def validate_code_interface(referral_code):
            """Handle referral code validation"""
            if not referral_code.strip():
                return "Please enter a referral code to validate."
            
            result = referral_system.validate_referral_code(referral_code)
            
            if result["valid"]:
                if result["owner"]:
                    response = f"""Referral Code Validation Result:

Code: {referral_code.upper()}
Status: VALID and AVAILABLE

Owner Information:
- Name: {result['owner']['name']}
- Customer ID: {result['owner']['id']}
- Phone: {result['owner']['phone']}

This code can be used for new customer registration.
The owner will receive credit when this code is used."""
                else:
                    response = f"Code validation: {result['message']}"
            else:
                response = f"Code validation failed: {result['message']}"
                response += f"""

Referral Code Format Requirements:
- Must be exactly 8 characters
- Format: AB1234R1 (2 letters + 4 digits + R + number 1-3)
- Examples: JO7890R1, SA3210R2, MI5678R3"""
            
            return response
        
        def chat_with_database(message, history):
            """Handle chat interface"""
            if not message.strip():
                return "", history
            
            response = chatbot.process_query(message)
            history.append((message, response))
            return "", history
        
        # Event Handlers for Database Management
        register_btn.click(
            register_customer_interface,
            inputs=[name_input, phone_input, referral_input],
            outputs=[registration_output]
        )
        
        clear_btn.click(
            lambda: ("", "", "", ""),
            outputs=[name_input, phone_input, referral_input, registration_output]
        )
        
        lookup_btn.click(
            lookup_customer_interface,
            inputs=[search_input],
            outputs=[lookup_output]
        )
        
        validate_btn.click(
            validate_code_interface,
            inputs=[code_input],
            outputs=[validation_output]
        )
        
        # Event Handlers for Chat Interface
        send_btn.click(
            chat_with_database,
            inputs=[chat_input, chat_interface],
            outputs=[chat_input, chat_interface]
        )
        
        chat_input.submit(
            chat_with_database,
            inputs=[chat_input, chat_interface],
            outputs=[chat_input, chat_interface]
        )
        
        gr.Markdown("""
        ---
        ### System Information:
        
        **Database Management Section:**
        - Register new customers with unique IDs
        - Generate 3 referral codes per customer
        - Track referral usage and discount eligibility
        - Search and validate customer information
        
        **Chat Interface Section:**
        - Ask questions about your business data
        - Get statistics and analytics
        - Find specific customer information
        - Monitor referral program performance
        
        **Data Storage:**
        All data is automatically saved to Excel files in the 'data' folder for backup and analysis.
        """)
    
    return demo

if __name__ == "__main__":
    print("Starting Tea Business Management System...")
    
    # Create and launch the application
    app = create_application()
    app.launch(
    server_name="0.0.0.0",  # This is the key change
    server_port=7860,
    share=False,
    debug=True,
    show_error=True
)
    
    print("Application is running on http://localhost:7860")