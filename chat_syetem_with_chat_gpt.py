import pandas as pd
import os
import requests
import json
from datetime import datetime

class DatabaseChatBot:
    """Optimized hybrid chat system with intelligent data filtering"""
    
    def __init__(self, referral_system):
        self.referral_system = referral_system
        self.db = referral_system.db
        
        # Setup OpenAI API
        self.setup_openai()
        
        # Conversation history
        self.conversation_history = []
        
        print("Optimized hybrid chat system initialized")
        if self.ai_enabled:
            print("✓ AI support enabled with smart data filtering")
        else:
            print("⚠ Running in rule-based mode only")
    
    def setup_openai(self):
        """Setup OpenAI API using requests"""
        self.ai_enabled = False
        
        try:
            # Get API key - directly use your key or from environment
            api_key = os.getenv('OPENAI_API_KEY')
            
            # If not in environment, use your actual key
            if not api_key:
                api_key = 'Enter your API key'
            
            if not api_key:
                print("No API key available. Running in rule-based mode only.")
                return
            
            self.api_key = api_key
            self.api_url = "https://api.openai.com/v1/chat/completions"
            
            # Test API key
            test_response = self.make_openai_request([
                {"role": "user", "content": "test"}
            ], max_tokens=1)
            
            if test_response:
                self.ai_enabled = True
                print("✓ OpenAI API configured successfully")
            else:
                print("API key test failed. Running in rule-based mode only.")
                
        except Exception as e:
            print(f"OpenAI setup failed: {e}")
            print("Running in rule-based mode only")
    
    def make_openai_request(self, messages, max_tokens=300, temperature=0.7):
        """Make direct API request to OpenAI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("API request timed out")
            return None
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    def fix_data_types(self):
        """Fix data types for calculations"""
        try:
            if not self.db.customers_df.empty:
                self.db.customers_df['referrals_completed'] = pd.to_numeric(
                    self.db.customers_df['referrals_completed'], 
                    errors='coerce'
                ).fillna(0).astype(int)
        except:
            pass
    
    def extract_customer_names_from_query(self, query):
        """Extract potential customer names from query"""
        words = query.split()
        potential_names = []
        
        # Skip common words
        skip_words = {
            'who', 'is', 'what', 'where', 'when', 'how', 'the', 'a', 'an', 
            'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'customer', 'customers', 'named', 'called', 'about', 'tell', 'me',
            'show', 'find', 'search', 'get', 'my', 'your', 'his', 'her'
        }
        
        for word in words:
            clean_word = word.strip('.,!?;:"()[]')
            if len(clean_word) > 2 and clean_word.lower() not in skip_words:
                potential_names.append(clean_word.title())
        
        return potential_names
    
    def get_relevant_customer_data(self, query):
        """Get only relevant customer data based on query"""
        if self.db.customers_df.empty:
            return None
        
        # Extract potential names from query
        potential_names = self.extract_customer_names_from_query(query)
        
        relevant_customers = []
        
        # If specific names mentioned, find those customers
        if potential_names:
            for name in potential_names:
                matches = self.db.customers_df[
                    self.db.customers_df['name'].str.contains(name, case=False, na=False)
                ]
                
                for _, customer in matches.iterrows():
                    customer_data = {
                        'name': customer['name'],
                        'id': customer['customer_id'],
                        'referrals': int(customer['referrals_completed']),
                        'discount': customer['discount_earned'],
                        'registration_date': customer['registration_date'][:10] if pd.notna(customer['registration_date']) else 'Unknown'
                    }
                    relevant_customers.append(customer_data)
        
        return relevant_customers if relevant_customers else None
    
    def get_summarized_business_context(self, query):
        """Get summarized business context - not full dataset"""
        try:
            customers_count = len(self.db.customers_df)
            referrals_count = len(self.db.referrals_df) if not self.db.referrals_df.empty else 0
            discount_customers = len(self.db.customers_df[self.db.customers_df['discount_earned'] == 'Yes']) if not self.db.customers_df.empty else 0
            
            # Get relevant customer data if names mentioned
            relevant_customers = self.get_relevant_customer_data(query)
            
            context = {
                "business_type": "Tea Business with Referral System",
                "total_customers": customers_count,
                "customers_with_discounts": discount_customers,
                "referral_requirement": "3 referrals needed for discount",
                "current_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add relevant customer data if found
            if relevant_customers:
                context["relevant_customers"] = relevant_customers
            
            # Add top performers summary if asking about performance
            query_lower = query.lower()
            if any(word in query_lower for word in ['top', 'best', 'performing', 'leader']):
                if not self.db.customers_df.empty:
                    top_3 = self.db.customers_df.nlargest(3, 'referrals_completed')
                    context["top_referrers"] = [
                        {
                            "name": row['name'], 
                            "referrals": int(row['referrals_completed']),
                            "discount": row['discount_earned']
                        } 
                        for _, row in top_3.iterrows()
                    ]
            
            return json.dumps(context, indent=2)
        except Exception as e:
            return f"Basic tea business with referral system. Context error: {e}"
    
    def should_use_ai(self, query):
        """Determine if query should use AI based on intermediate rules"""
        query_lower = query.lower()
        
        # Definite rule-based queries (high confidence data queries)
        rule_based_patterns = [
            ['how', 'many', 'customers'], 
            ['total', 'customers'],
            ['customer', 'count'],
            ['customers', 'with', 'discount'],
            ['top', 'referrer'],
            ['best', 'referrer'], 
            ['most', 'referral'],
            ['recent', 'customer'],
            ['new', 'customer'],
            ['latest', 'customer'],
            ['referral', 'code'],
            ['codes', 'used'],
            ['success', 'rate'],
            ['conversion'],
            ['percentage'],
            ['statistics'],
            ['stats'],
            ['overview'],
            ['summary']
        ]
        
        # Check if it's a definite rule-based query
        for pattern in rule_based_patterns:
            if all(word in query_lower for word in pattern):
                return False
        
        # Customer search patterns (rule-based)
        search_patterns = [
            ['find', 'customer'],
            ['search', 'customer'], 
            ['customer', 'named'],
            ['show', 'customer']
        ]
        
        for pattern in search_patterns:
            if all(word in query_lower for word in pattern):
                return False
        
        # AI-suitable queries (conversational, advice, general knowledge)
        ai_patterns = [
            ['what', 'tea'], ['which', 'tea'], ['recommend', 'tea'],
            ['how', 'brew'], ['brewing'], ['steep'],
            ['business', 'advice'], ['improve'], ['strategy'],
            ['customer', 'service'], ['retention'],
            ['marketing'], ['promotion'], ['grow'],
            ['hello'], ['hi'], ['thanks'], ['thank', 'you']
        ]
        
        for pattern in ai_patterns:
            if any(all(word in query_lower for word in pattern) for pattern in [pattern]):
                return True
        
        # If query mentions customer names but isn't a search command, use AI with data
        potential_names = self.extract_customer_names_from_query(query)
        if potential_names and not any(word in query_lower for word in ['find', 'search', 'show']):
            return True
        
        # Default to AI for conversational queries
        return True
    
    def process_query(self, query):
        """Main query processing with optimized hybrid approach"""
        if not query.strip():
            return "Please ask me a question about your tea business!"
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        query_lower = query.lower()
        self.fix_data_types()
        
        # Decide whether to use rule-based or AI
        if not self.should_use_ai(query):
            # Use rule-based for data queries
            rule_response = self.try_rule_based_response(query_lower, query)
            if rule_response:
                self.conversation_history.append({"role": "assistant", "content": rule_response})
                return rule_response
        
        # Use AI for conversational queries with relevant data
        if self.ai_enabled:
            ai_response = self.get_ai_response_with_data(query)
            if ai_response:
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                return ai_response
        
        # Final fallback to rule-based
        rule_response = self.try_rule_based_response(query_lower, query)
        if rule_response:
            self.conversation_history.append({"role": "assistant", "content": rule_response})
            return rule_response
        
        # Ultimate fallback
        help_response = self.get_help_response()
        self.conversation_history.append({"role": "assistant", "content": help_response})
        return help_response
    
    def get_ai_response_with_data(self, query):
        """Get AI response with only relevant data"""
        if not self.ai_enabled:
            return None
        
        try:
            # Get summarized context with relevant data only
            business_context = self.get_summarized_business_context(query)
            
            system_message = f"""You are a helpful assistant for a tea business with a referral system.

Current Business Context:
{business_context}

Guidelines:
- Be friendly and professional
- Focus on tea business topics
- Keep responses concise but helpful
- Use the provided customer data when relevant
- If specific customer data is provided, reference it accurately
- For data-heavy queries, suggest using specific commands like "show me statistics"
- You can discuss tea varieties, brewing methods, business advice
"""
            
            messages = [{"role": "system", "content": system_message}]
            
            # Add recent conversation history
            recent_history = self.conversation_history[-6:]
            messages.extend(recent_history)
            
            return self.make_openai_request(messages)
            
        except Exception as e:
            print(f"AI Error: {e}")
            return None
    
    def try_rule_based_response(self, query_lower, original_query):
        """Try to match query with rule-based responses"""
        
        if any(phrase in query_lower for phrase in ['how many customers', 'total customers', 'customer count']):
            return self.get_customer_count()
        
        elif any(phrase in query_lower for phrase in ['customers with discount', 'discounts', 'discount earned']):
            return self.get_discount_customers()
        
        elif any(phrase in query_lower for phrase in ['top referrer', 'best referrer', 'most referral']):
            return self.get_top_referrers()
        
        elif any(phrase in query_lower for phrase in ['recent', 'recently', 'new customer', 'latest']):
            return self.get_recent_customers()
        
        elif any(phrase in query_lower for phrase in ['referral code', 'codes used', 'referral usage']):
            return self.get_referral_status()
        
        elif any(phrase in query_lower for phrase in ['success rate', 'conversion', 'percentage']):
            return self.get_success_rates()
        
        elif any(phrase in query_lower for phrase in ['find customer', 'search customer', 'customer named']):
            return self.find_customer_in_query(original_query)
        
        elif any(phrase in query_lower for phrase in ['statistics', 'stats', 'overview', 'summary']):
            return self.get_general_stats()
        
        return None
    
    # Keep all your existing rule-based methods unchanged
    def find_customer_in_query(self, query):
        """Extract customer name from query and find them"""
        if self.db.customers_df.empty:
            return "No customers registered yet."
        
        words = query.split()
        name_candidates = []
        
        common_words = {'find', 'customer', 'named', 'called', 'search', 'show', 'me', 'the', 'for', 'with', 'name', 'who', 'is'}
        for word in words:
            if len(word) > 2 and word.lower() not in common_words:
                name_candidates.append(word.lower())
        
        if not name_candidates:
            return "Please specify the customer name you're looking for."
        
        results = []
        for _, customer in self.db.customers_df.iterrows():
            customer_name = str(customer['name']).lower()
            if any(candidate in customer_name for candidate in name_candidates):
                results.append(customer)
        
        if not results:
            return f"No customers found matching '{' '.join(name_candidates)}'."
        
        result = f"Found {len(results)} customer(s):\n\n"
        for customer in results:
            referrals = int(customer['referrals_completed'])
            result += f"• {customer['name']} (ID: {customer['customer_id']})\n"
            result += f"  Phone: {customer['phone']}\n"
            result += f"  Referrals: {referrals}/3\n"
            result += f"  Discount: {customer['discount_earned']}\n\n"
        
        return result

    def get_customer_count(self):
        """Get total customer count"""
        total = len(self.db.customers_df)
        if total == 0:
            return "You have no customers registered yet."
        return f"You have {total} customers registered in your tea business database."
    
    def get_discount_customers(self):
        """Get customers with discounts"""
        if self.db.customers_df.empty:
            return "No customers registered yet."
        
        discount_customers = self.db.customers_df[self.db.customers_df['discount_earned'] == 'Yes']
        total = len(self.db.customers_df)
        discount_count = len(discount_customers)
        
        if discount_count == 0:
            return f"No customers have earned discounts yet out of {total} total customers."
        
        result = f"Customers with discounts ({discount_count} out of {total}):\n\n"
        for _, customer in discount_customers.iterrows():
            referrals = int(customer['referrals_completed'])
            result += f"• {customer['name']} (ID: {customer['customer_id']}) - {referrals}/3 referrals completed\n"
        
        return result
    
    def get_top_referrers(self):
        """Get top referring customers"""
        if self.db.customers_df.empty:
            return "No customers registered yet."
        
        top_customers = self.db.customers_df.sort_values('referrals_completed', ascending=False).head(5)
        
        result = "Top 5 Referrers:\n\n"
        for i, (_, customer) in enumerate(top_customers.iterrows(), 1):
            referrals = int(customer['referrals_completed'])
            status = "DISCOUNT EARNED" if customer['discount_earned'] == 'Yes' else "In Progress"
            result += f"{i}. {customer['name']} - {referrals}/3 referrals ({status})\n"
        
        return result
    
    def get_recent_customers(self):
        """Get recent customers"""
        if self.db.customers_df.empty:
            return "No customers registered yet."
        
        recent = self.db.customers_df.tail(5)
        result = "Recent customers (last 5):\n\n"
        
        for _, customer in recent.iterrows():
            date = customer['registration_date'][:10] if pd.notna(customer['registration_date']) else 'Unknown'
            result += f"• {customer['name']} (ID: {customer['customer_id']}) - Registered: {date}\n"
        
        return result
    
    def get_referral_status(self):
        """Get referral code status"""
        if self.db.referrals_df.empty:
            return "No referral codes generated yet."
        
        total_codes = len(self.db.referrals_df)
        used_codes = len(self.db.referrals_df[self.db.referrals_df['status'] == 'Used'])
        available_codes = total_codes - used_codes
        
        result = f"Referral Code Status:\n\n"
        result += f"• Total referral codes: {total_codes}\n"
        result += f"• Used codes: {used_codes}\n"
        result += f"• Available codes: {available_codes}\n"
        result += f"• Usage rate: {(used_codes/total_codes*100):.1f}%\n"
        
        return result
    
    def get_success_rates(self):
        """Get success rates"""
        if self.db.customers_df.empty:
            return "No data available for rate calculations."
        
        total_customers = len(self.db.customers_df)
        customers_with_discount = len(self.db.customers_df[self.db.customers_df['discount_earned'] == 'Yes'])
        
        total_codes = len(self.db.referrals_df)
        used_codes = len(self.db.referrals_df[self.db.referrals_df['status'] == 'Used']) if not self.db.referrals_df.empty else 0
        
        result = "Success Rates:\n\n"
        result += f"• Discount Achievement Rate: {(customers_with_discount/total_customers*100):.1f}%\n"
        if total_codes > 0:
            result += f"• Referral Code Usage Rate: {(used_codes/total_codes*100):.1f}%\n"
        result += f"• Customers with Discounts: {customers_with_discount}/{total_customers}\n"
        
        return result
    
    def get_general_stats(self):
        """Get general statistics"""
        customers = len(self.db.customers_df)
        referrals = len(self.db.referrals_df)
        used_referrals = len(self.db.referrals_df[self.db.referrals_df['status'] == 'Used']) if not self.db.referrals_df.empty else 0
        discounts = len(self.db.customers_df[self.db.customers_df['discount_earned'] == 'Yes']) if not self.db.customers_df.empty else 0
        
        result = f"Tea Business Statistics:\n\n"
        result += f"Total Customers: {customers}\n"
        result += f"Total Referral Codes: {referrals}\n"
        result += f"Used Referral Codes: {used_referrals}\n"
        result += f"Customers with Discounts: {discounts}\n"
        
        if customers > 0:
            result += f"Discount Rate: {(discounts/customers*100):.1f}%\n"
        if referrals > 0:
            result += f"Code Usage Rate: {(used_referrals/referrals*100):.1f}%\n"
        
        return result
    
    def get_help_response(self):
        """Help response"""
        help_text = """I can help you with your tea business! Here are some things you can ask:

Data & Statistics (Rule-based - Fast & Accurate):
- "How many customers do I have?"
- "Show me general statistics"
- "What's my success rate?"
- "Who are my top referrers?"
- "Find customer named [name]"

General Chat (AI-powered):
- Ask about tea varieties and recommendations
- Get business advice and tips
- Discuss brewing techniques
- Customer service strategies
"""
        
        return help_text