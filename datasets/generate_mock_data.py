import csv
import os

# URLs mock dataset
def generate_mock_urls():
    urls = [
        # Phishing (label 1)
        ("http://secure-login-paypal.com/verify", 1),
        ("https://update.apple-support-id.com/login", 1),
        ("http://192.168.1.1/login.php", 1),
        ("http://bit.ly/secure-login", 1),
        ("https://amazon-security-alert.net/auth", 1),
        ("http://free-gift-card-win.com", 1),
        ("https://netflix-payment-update.info", 1),
        ("http://chase-bank-verify-account.com", 1),
        ("http://www.google-security-update.com", 1),
        ("http://login-microsoftonline.com.secure-auth.net", 1),
        
        # Legitimate (label 0)
        ("https://www.google.com", 0),
        ("https://github.com/login", 0),
        ("https://www.amazon.com/gp/cart/view.html", 0),
        ("https://www.netflix.com/browse", 0),
        ("https://en.wikipedia.org/wiki/Main_Page", 0),
        ("https://stackoverflow.com/questions", 0),
        ("https://www.apple.com/support/", 0),
        ("https://www.paypal.com/us/home", 0),
        ("https://www.chase.com/", 0),
        ("https://www.microsoft.com/en-us/", 0),
    ]
    
    # Repeat for more samples (for training pipeline to work without issues)
    urls = urls * 20
    
    os.makedirs("datasets", exist_ok=True)
    with open("datasets/urls.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "label"])
        writer.writerows(urls)
    
    print(f"Generated {len(urls)} URL samples in datasets/urls.csv")

# Emails mock dataset
def generate_mock_emails():
    emails = [
        # Phishing (label 1)
        ("URGENT: Your account will be suspended! Please verify your details at http://secure-login-paypal.com/verify immediately.", 1),
        ("You have won a $1000 Amazon gift card! Click here http://free-gift-card-win.com to claim your prize now.", 1),
        ("Security Alert: We detected unusual activity. Update your billing info at https://update.apple-support-id.com/login.", 1),
        ("Your invoice is attached. Please review the payment details to avoid late fees.", 1),
        ("Dear customer, your password expires in 24 hours. Reset it using this link: http://bit.ly/secure-login", 1),
        
        # Legitimate (label 0)
        ("Hi team, please find the meeting notes attached. Let me know if you have any questions.", 0),
        ("Your GitHub password was successfully changed. If this wasn't you, please contact support.", 0),
        ("Thank you for your Amazon order! Your package will arrive by Tuesday.", 0),
        ("Reminder: Team lunch tomorrow at 12 PM. See you there!", 0),
        ("The quarterly report has been updated and is available on the shared drive.", 0),
    ]
    
    # Repeat for more samples
    emails = emails * 40
    
    with open("datasets/emails.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(emails)
    
    print(f"Generated {len(emails)} Email samples in datasets/emails.csv")

if __name__ == "__main__":
    generate_mock_urls()
    generate_mock_emails()
