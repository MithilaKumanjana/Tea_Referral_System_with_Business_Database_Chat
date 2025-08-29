import pandas as pd
import re
from datetime import datetime
import os

class TeaBusinessDatabase:
    """Complete database system for tea business referral management"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        self.customers_file = os.path.join(data_dir, "tea_customers.xlsx")
        self.referrals_file = os.path.join(data_dir, "tea_referrals.xlsx")
        self.sales_file = os.path.join(data_dir, "tea_sales.xlsx")
        
        self.initialize_databases()
        print("Tea Business Database System initialized")
    
    def initialize_databases(self):
        """Initialize all database files"""
        self.customers_df = self.load_or_create_customers()
        self.referrals_df = self.load_or_create_referrals()
        self.sales_df = self.load_or_create_sales()
    
    def load_or_create_customers(self):
        """Load or create customer database"""
        if os.path.exists(self.customers_file):
            try:
                df = pd.read_excel(self.customers_file)
                print(f"Loaded {len(df)} customers from database")
                return df
            except:
                print("Error loading customer database, creating new one")
        
        customer_data = {
            'customer_id': [],
            'name': [],
            'phone': [],
            'registration_date': [],
            'referral_code_1': [],
            'referral_code_2': [],
            'referral_code_3': [],
            'referrals_completed': [],
            'discount_earned': [],
            'referred_by': [],
            'status': [],
            'total_purchases': [],
            'notes': []
        }
        
        df = pd.DataFrame(customer_data)
        df.to_excel(self.customers_file, index=False)
        print("Created new customer database")
        return df
    
    def load_or_create_referrals(self):
        """Load or create referral database"""
        if os.path.exists(self.referrals_file):
            try:
                df = pd.read_excel(self.referrals_file)
                print(f"Loaded {len(df)} referral codes from database")
                return df
            except:
                print("Error loading referral database, creating new one")
        
        referral_data = {
            'referral_code': [],
            'owner_customer_id': [],
            'owner_name': [],
            'owner_phone': [],
            'used_by_customer_id': [],
            'used_by_name': [],
            'used_by_phone': [],
            'date_used': [],
            'status': [],
            'discount_applied': [],
            'notes': []
        }
        
        df = pd.DataFrame(referral_data)
        df.to_excel(self.referrals_file, index=False)
        print("Created new referral database")
        return df
    
    def load_or_create_sales(self):
        """Load or create sales database"""
        if os.path.exists(self.sales_file):
            try:
                df = pd.read_excel(self.sales_file)
                print(f"Loaded {len(df)} sales records from database")
                return df
            except:
                print("Error loading sales database, creating new one")
        
        sales_data = {
            'sale_id': [],
            'customer_id': [],
            'customer_name': [],
            'sale_date': [],
            'items_purchased': [],
            'total_amount': [],
            'discount_applied': [],
            'discount_amount': [],
            'referral_code_used': [],
            'payment_method': [],
            'notes': []
        }
        
        df = pd.DataFrame(sales_data)
        df.to_excel(self.sales_file, index=False)
        print("Created new sales database")
        return df
    
    def save_databases(self):
        """Save all databases"""
        try:
            self.customers_df.to_excel(self.customers_file, index=False)
            self.referrals_df.to_excel(self.referrals_file, index=False)
            self.sales_df.to_excel(self.sales_file, index=False)
            print("All databases saved successfully")
            return True
        except Exception as e:
            print(f"Error saving databases: {e}")
            return False

class ReferralSystem:
    """Referral management system"""
    
    def __init__(self, database):
        self.db = database
    
    def generate_customer_id(self, name, phone):
        """Generate unique customer ID"""
        name_clean = re.sub(r'[^a-zA-Z]', '', name.strip())
        name_part = (name_clean[:2] if len(name_clean) >= 2 else name_clean + "XX").upper()
        
        phone_clean = re.sub(r'[^0-9]', '', phone.strip())
        phone_part = phone_clean[-4:] if len(phone_clean) >= 4 else phone_clean.ljust(4, '0')
        
        return f"{name_part}{phone_part}"
    
    def generate_referral_codes(self, customer_id):
        """Generate 3 referral codes"""
        return [f"{customer_id}R1", f"{customer_id}R2", f"{customer_id}R3"]
    
    def validate_input(self, name, phone):
        """Validate customer input"""
        errors = []
        
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        phone_clean = re.sub(r'[^0-9]', '', phone) if phone else ""
        if not phone_clean or len(phone_clean) < 4:
            errors.append("Phone number must have at least 4 digits")
        
        return errors, name.strip().title(), phone_clean
    
    def customer_exists(self, name, phone):
        """Check if customer already exists"""
        customer_id = self.generate_customer_id(name, phone)
        existing = self.db.customers_df[self.db.customers_df['customer_id'] == customer_id]
        return not existing.empty, customer_id
    
    def validate_referral_code(self, referral_code):
        """Validate referral code"""
        if not referral_code or not referral_code.strip():
            return {"valid": True, "message": "No referral code provided", "owner": None}
        
        code = referral_code.strip().upper()
        
        if not re.match(r'^[A-Z]{2}\d{4}R[123]$', code):
            return {"valid": False, "message": "Invalid referral code format"}
        
        existing = self.db.referrals_df[self.db.referrals_df['referral_code'] == code]
        
        if existing.empty:
            return {"valid": False, "message": "Referral code not found"}
        
        referral_info = existing.iloc[0]
        
        if referral_info['status'] == 'Used':
            return {"valid": False, "message": f"Code already used by {referral_info['used_by_name']}"}
        
        return {
            "valid": True,
            "message": f"Valid code from {referral_info['owner_name']}",
            "owner": {
                "id": referral_info['owner_customer_id'],
                "name": referral_info['owner_name'],
                "phone": referral_info['owner_phone']
            }
        }
    
    def register_customer(self, name, phone, referral_code=None):
        """Register new customer"""
        # Validate input
        errors, clean_name, clean_phone = self.validate_input(name, phone)
        if errors:
            return {"success": False, "message": "; ".join(errors)}
        
        # Check if exists
        exists, customer_id = self.customer_exists(clean_name, clean_phone)
        if exists:
            return {"success": False, "message": f"Customer already exists with ID: {customer_id}"}
        
        # Validate referral code
        referred_by = "Direct Customer"
        referral_owner = None
        
        if referral_code and referral_code.strip():
            validation = self.validate_referral_code(referral_code)
            if not validation["valid"]:
                return {"success": False, "message": validation["message"]}
            
            if validation["owner"]:
                referral_owner = validation["owner"]
                referred_by = f"Referred by {referral_owner['name']}"
        
        # Create customer
        referral_codes = self.generate_referral_codes(customer_id)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        new_customer = {
            'customer_id': customer_id,
            'name': clean_name,
            'phone': clean_phone,
            'registration_date': current_time,
            'referral_code_1': referral_codes[0],
            'referral_code_2': referral_codes[1],
            'referral_code_3': referral_codes[2],
            'referrals_completed': 0,
            'discount_earned': 'No',
            'referred_by': referred_by,
            'status': 'Active',
            'total_purchases': 0,
            'notes': ''
        }
        
        # Add to database
        self.db.customers_df = pd.concat([self.db.customers_df, pd.DataFrame([new_customer])], ignore_index=True)
        
        # Add referral codes
        for code in referral_codes:
            new_referral = {
                'referral_code': code,
                'owner_customer_id': customer_id,
                'owner_name': clean_name,
                'owner_phone': clean_phone,
                'used_by_customer_id': '',
                'used_by_name': '',
                'used_by_phone': '',
                'date_used': '',
                'status': 'Available',
                'discount_applied': 'No',
                'notes': ''
            }
            self.db.referrals_df = pd.concat([self.db.referrals_df, pd.DataFrame([new_referral])], ignore_index=True)
        
        # Process referral usage
        if referral_code and referral_owner:
            self.use_referral_code(referral_code.strip(), customer_id, clean_name, clean_phone)
        
        # Save databases
        self.db.save_databases()
        
        return {
            "success": True,
            "customer_id": customer_id,
            "referral_codes": referral_codes,
            "customer_data": new_customer,
            "message": "Customer registered successfully!"
        }
    
    def use_referral_code(self, referral_code, customer_id, customer_name, customer_phone):
        """Mark referral code as used"""
        code = referral_code.strip().upper()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        referral_idx = self.db.referrals_df[self.db.referrals_df['referral_code'] == code].index
        
        if not referral_idx.empty:
            idx = referral_idx[0]
            
            self.db.referrals_df.loc[idx, 'used_by_customer_id'] = customer_id
            self.db.referrals_df.loc[idx, 'used_by_name'] = customer_name
            self.db.referrals_df.loc[idx, 'used_by_phone'] = customer_phone
            self.db.referrals_df.loc[idx, 'date_used'] = current_time
            self.db.referrals_df.loc[idx, 'status'] = 'Used'
            
            owner_id = self.db.referrals_df.loc[idx, 'owner_customer_id']
            self.update_referral_progress(owner_id)
    
    def update_referral_progress(self, customer_id):
        """Update customer referral progress"""
        used_count = len(self.db.referrals_df[
            (self.db.referrals_df['owner_customer_id'] == customer_id) & 
            (self.db.referrals_df['status'] == 'Used')
        ])
        
        customer_idx = self.db.customers_df[self.db.customers_df['customer_id'] == customer_id].index
        
        if not customer_idx.empty:
            idx = customer_idx[0]
            self.db.customers_df.loc[idx, 'referrals_completed'] = used_count
            
            if used_count >= 3:
                self.db.customers_df.loc[idx, 'discount_earned'] = 'Yes'
                customer_name = self.db.customers_df.loc[idx, 'name']
                print(f"{customer_name} earned discount! (3/3 referrals completed)")
    
    def get_customer_info(self, search_term):
        """Get customer information"""
        search_term = str(search_term).strip()
        
        if not search_term:
            return {"found": False, "message": "Please provide search term"}
        
        # Search by ID
        customer = self.db.customers_df[
            self.db.customers_df['customer_id'].str.contains(search_term, case=False, na=False)
        ]
        
        # Search by name
        if customer.empty:
            customer = self.db.customers_df[
                self.db.customers_df['name'].str.contains(search_term, case=False, na=False)
            ]
        
        # Search by phone
        if customer.empty:
            customer = self.db.customers_df[
                self.db.customers_df['phone'].str.contains(search_term, na=False)
            ]
        
        if customer.empty:
            return {"found": False, "message": f"Customer not found: {search_term}"}
        
        customer_info = customer.iloc[0]
        referral_details = self.get_referral_details(customer_info['customer_id'])
        
        return {
            "found": True,
            "customer": customer_info,
            "referral_details": referral_details
        }
    
    def get_referral_details(self, customer_id):
        """Get referral usage details"""
        referrals = self.db.referrals_df[self.db.referrals_df['owner_customer_id'] == customer_id]
        
        details = []
        for _, referral in referrals.iterrows():
            status = "Used" if referral['status'] == 'Used' else "Available"
            used_info = f"Used by {referral['used_by_name']} on {referral['date_used'][:10]}" if referral['status'] == 'Used' else "Available for sharing"
            
            details.append({
                'code': referral['referral_code'],
                'status': referral['status'],
                'used_info': used_info,
                'used_by_name': referral['used_by_name'] if referral['status'] == 'Used' else '',
                'date_used': referral['date_used'][:10] if referral['date_used'] else ''
            })
        
        return details