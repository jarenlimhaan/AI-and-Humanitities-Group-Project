import cv2
import numpy as np
import pytesseract
from PIL import Image


class ScreenshotAnalyzer:
    def __init__(self):
        # Expanded keywords to identify more digibank pages/features
        self.page_keywords = {
            'login': ['login', 'username', 'password', 'otp', 'signin', 'face id', 'fingerprint'],
            'account_summary': ['account', 'balance', 'transactions', 'statement', 'savings', 'checking', 'fixed deposit'],
            'transfer': ['transfer', 'recipient', 'amount', 'paynow', 'fast', 'giro', 'international', 'remittance'],
            'bill_payment': ['bill', 'payment', 'payee', 'utilities', 'mobile', 'overdue', 'due'],
            'investment': ['investment', 'portfolio', 'mutual funds', 'bonds', 'equities', 'goal savings'],
            'credit_card': ['credit card', 'rewards', 'points', 'limit', 'redeem', 'repayment', 'due'],
            'loan': ['loan', 'mortgage', 'repayment', 'personal loan', 'home loan', 'interest rate'],
            'qr_payment': ['qr code', 'paynow', 'tap-to-pay', 'virtual wallet', 'apple pay', 'google pay'],
            'settings': ['settings', 'profile', 'security', 'password', 'biometric', 'notifications', 'privacy'],
            'insurance': ['insurance', 'travel', 'policy', 'health', 'activate overseas usage'],
            'customer_service': ['customer service', 'help', 'support', 'chatbot', 'complaint', 'dispute'],
            'alerts': ['alert', 'notification', 'blocked', 'fraud', 'session expired'],
            'dbs_homepage': ['dbs', 'bank', 'singapore', 'group', 'investor', 'careers', 'products'],
            'logout': ['logout', 'sign out', 'session timeout', 're-login']
        }

        # Updated navigation instructions for identified pages
        self.navigation_instructions = {
            'login': "To log in, enter your username and password, or use biometric authentication if available.",
            'account_summary': "This is your account summary. Select an account to view details or download statements.",
            'transfer': (
                "To transfer funds, select the source account, choose a recipient, enter the amount, "
                "and tap 'Transfer'. Use PayNow or FAST for quick transfers."
            ),
            'bill_payment': "Pay your bills by selecting a payee, entering the amount, and tapping 'Pay'.",
            'investment': "You're on the investment page. View your portfolio or buy/sell mutual funds and equities.",
            'credit_card': "Manage your credit card here. Adjust your limit, redeem points, or make repayments.",
            'loan': "This is the loan section. View repayment schedules or apply for a new loan.",
            'qr_payment': "You're on the QR payment page. Scan a QR code or use tap-to-pay to complete your purchase.",
            'settings': "Update your profile, change security settings, or adjust notification preferences.",
            'insurance': "Manage your insurance policies or activate overseas usage for your cards.",
            'customer_service': "Need help? Contact customer service or chat with our support chatbot.",
            'alerts': "You've received an alert. Review any blocked transactions or session timeouts.",
            'dbs_homepage': (
                "You're on the DBS homepage. Explore products, log in, or access banking services through the menu."
            ),
            'logout': "You are logged out. Please log in again to access your account."
        }

    def preprocess_image(self, image):
        """Convert image to grayscale and apply thresholding."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return thresh

    def extract_text(self, image):
        """Extract text from the preprocessed image using Tesseract OCR."""
        preprocessed = self.preprocess_image(image)
        text = pytesseract.image_to_string(Image.fromarray(preprocessed))
        return text.lower()

    def identify_page(self, text):
        """Identify the page based on the number of matching keywords."""
        max_matches = 0
        identified_page = None

        for page, keywords in self.page_keywords.items():
            matches = sum(keyword in text for keyword in keywords)
            if matches > max_matches:
                max_matches = matches
                identified_page = page

        return identified_page

    def analyze_screenshot(self, image_path):
        """Analyze the screenshot and provide relevant instructions."""
        image = cv2.imread(image_path)
        extracted_text = self.extract_text(image)
        identified_page = self.identify_page(extracted_text)

        if identified_page:
            return self.navigation_instructions[identified_page]
        else:
            return (
                "I'm sorry, I couldn't identify this page. "
                "Please provide more details about what you're trying to do."
            )

    def print_extracted_text(self, image_path):
        """Print the extracted text from the image for debugging."""
        image = cv2.imread(image_path)
        extracted_text = self.extract_text(image)
        print("Extracted text:")
        print(extracted_text)
