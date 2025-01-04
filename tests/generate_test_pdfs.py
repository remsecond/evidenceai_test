from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pathlib import Path
import os

def create_valid_pdf(output_path: Path, num_messages: int = 5):
    """Create a valid OFW PDF with specified number of messages"""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    
    # Header
    c.drawString(72, 750, "OurFamilyWizard")
    c.drawString(72, 730, "Message Report")
    c.drawString(72, 710, "Generated: 12/01/2024 at 09:00 AM")
    c.drawString(72, 690, f"Number of messages: {num_messages}")
    c.drawString(72, 670, "Timezone: America/Los_Angeles")
    c.drawString(72, 650, "Parents: Person A, Person B")
    c.drawString(72, 630, "Child(ren): Child A, Child B")
    c.drawString(72, 610, "Third Party: Mediator")
    
    # Messages
    y = 550
    for i in range(num_messages):
        c.drawString(72, y, f"Message {i+1} of {num_messages}")
        c.drawString(72, y-20, f"Sent: 12/01/2024 at {i+1:02d}:00 AM")
        c.drawString(72, y-40, "From: Person A")
        c.drawString(72, y-60, "To: Person B (First Viewed: 12/01/2024 at 10:00 AM)")
        c.drawString(72, y-80, f"Subject: Test Message {i+1}")
        c.drawString(72, y-100, f"Sample message content for message {i+1}")
        
        y -= 140
        if y < 72:  # Start new page if needed
            c.showPage()
            y = 750
    
    c.save()

def create_invalid_pdf(output_path: Path, issue: str):
    """Create an invalid PDF with specific issues"""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    
    if issue == 'missing_headers':
        # Skip headers, only add messages
        c.drawString(72, 750, "Message 1 of 1")
        c.drawString(72, 730, "Sample content")
        
    elif issue == 'malformed_dates':
        # Add headers with invalid dates
        c.drawString(72, 750, "OurFamilyWizard")
        c.drawString(72, 730, "Message Report")
        c.drawString(72, 710, "Generated: Invalid Date")
        c.drawString(72, 690, "Number of messages: 1")
        
        # Message with invalid date
        c.drawString(72, 650, "Message 1 of 1")
        c.drawString(72, 630, "Sent: Not a valid date")
        
    elif issue == 'incomplete_messages':
        # Add headers
        c.drawString(72, 750, "OurFamilyWizard")
        c.drawString(72, 730, "Message Report")
        c.drawString(72, 710, "Generated: 12/01/2024 at 09:00 AM")
        c.drawString(72, 690, "Number of messages: 1")
        
        # Incomplete message (missing required fields)
        c.drawString(72, 650, "Message 1 of 1")
        c.drawString(72, 630, "From: Person A")
        # Missing To, Sent, Subject fields
        
    c.save()

def create_edge_case_pdf(output_path: Path, case: str):
    """Create PDFs with edge cases"""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    
    # Add standard headers
    c.drawString(72, 750, "OurFamilyWizard")
    c.drawString(72, 730, "Message Report")
    c.drawString(72, 710, "Generated: 12/01/2024 at 09:00 AM")
    
    if case == 'long_thread':
        # Create a very long thread of related messages
        num_messages = 50
        c.drawString(72, 690, f"Number of messages: {num_messages}")
        
        y = 650
        for i in range(num_messages):
            c.drawString(72, y, f"Message {i+1} of {num_messages}")
            c.drawString(72, y-20, f"Sent: 12/01/2024 at {i+1:02d}:00 AM")
            c.drawString(72, y-40, "From: Person A")
            c.drawString(72, y-60, "To: Person B")
            c.drawString(72, y-80, "Subject: Re: Long Thread")
            
            y -= 120
            if y < 72:
                c.showPage()
                y = 750
                
    elif case == 'special_characters':
        # Create messages with special characters
        c.drawString(72, 690, "Number of messages: 1")
        c.drawString(72, 650, "Message 1 of 1")
        c.drawString(72, 630, "Sent: 12/01/2024 at 09:00 AM")
        c.drawString(72, 610, "From: Person © Å")
        c.drawString(72, 590, "To: Person ß ™")
        c.drawString(72, 570, "Subject: Special © ™ ® Characters")
        c.drawString(72, 550, "Content with åßđŋħ characters")
        
    elif case == 'nested_replies':
        # Create a chain of nested replies
        num_messages = 5
        c.drawString(72, 690, f"Number of messages: {num_messages}")
        
        y = 650
        previous_content = ""
        for i in range(num_messages):
            c.drawString(72, y, f"Message {i+1} of {num_messages}")
            c.drawString(72, y-20, f"Sent: 12/01/2024 at {i+1:02d}:00 AM")
            c.drawString(72, y-40, f"From: Person {'A' if i % 2 == 0 else 'B'}")
            c.drawString(72, y-60, f"To: Person {'B' if i % 2 == 0 else 'A'}")
            c.drawString(72, y-80, "Subject: Re: Nested Thread")
            
            current_content = f"Reply level {i+1}"
            if previous_content:
                current_content += f"\n\nOn 12/01/2024...\n{previous_content}"
            c.drawString(72, y-100, current_content)
            
            previous_content = current_content
            y -= 140
            if y < 72:
                c.showPage()
                y = 750
    
    c.save()

def main():
    """Generate all test PDFs"""
    test_dir = Path("C:/Users/robmo/OneDrive/Documents/evidenceai_test/tests/test_input")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create valid PDFs
    create_valid_pdf(test_dir / "valid_basic.pdf", num_messages=5)
    create_valid_pdf(test_dir / "valid_large.pdf", num_messages=20)
    
    # Create invalid PDFs
    create_invalid_pdf(test_dir / "invalid_missing_headers.pdf", "missing_headers")
    create_invalid_pdf(test_dir / "invalid_malformed_dates.pdf", "malformed_dates")
    create_invalid_pdf(test_dir / "invalid_incomplete_messages.pdf", "incomplete_messages")
    
    # Create edge case PDFs
    create_edge_case_pdf(test_dir / "edge_long_thread.pdf", "long_thread")
    create_edge_case_pdf(test_dir / "edge_special_chars.pdf", "special_characters")
    create_edge_case_pdf(test_dir / "edge_nested_replies.pdf", "nested_replies")
    
    print("Generated test PDFs in:", test_dir)

if __name__ == "__main__":
    main()