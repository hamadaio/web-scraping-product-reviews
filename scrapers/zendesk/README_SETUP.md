# Zendesk API Configuration Template
# 
# Copy this file to `zendesk_config.js` and fill in your actual credentials
# DO NOT commit the actual config file with real credentials to version control

# Your Zendesk Configuration:
# 1. Subdomain: The part before .zendesk.com in your Zendesk URL
#    Example: If your Zendesk is at https://mendi.zendesk.com, then subdomain = 'mendi'

# 2. Email: Your Zendesk admin email address

# 3. API Token: 
#    - Go to Zendesk Admin Center
#    - Navigate to Apps and integrations > APIs > Zendesk API
#    - Enable token access and generate a new token
#    - Copy the token value

# Update the ZENDESK_CONFIG object in zendesk_tickets_scraper.js with:

const ZENDESK_CONFIG = {
  subdomain: 'your-subdomain',           // Replace with your actual subdomain
  email: 'your-email@domain.com',        // Replace with your Zendesk admin email  
  apiToken: 'your-api-token',            // Replace with your generated API token
  
  // These don't need to be changed
  baseUrl: 'https://{subdomain}.zendesk.com/api/v2',
  endpoints: {
    tickets: '/tickets.json',
    satisfaction_ratings: '/satisfaction_ratings.json',
    users: '/users.json'
  }
};

# Security Notes:
# - Keep your API token secret
# - Consider using environment variables for production
# - The API token has the same permissions as your user account
# - You can regenerate the token if it gets compromised

# Rate Limits:
# - Zendesk allows 700 requests per minute
# - The scraper includes automatic rate limiting delays
# - For large datasets, the scraper may take several minutes to complete
