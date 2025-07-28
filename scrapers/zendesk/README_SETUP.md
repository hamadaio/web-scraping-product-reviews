# Zendesk API Configuration Setup

## Security Options (Choose One)

### Option 1: Environment Variables (Recommended)
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```
   ZENDESK_SUBDOMAIN=your-subdomain
   ZENDESK_EMAIL=your-email@domain.com
   ZENDESK_API_TOKEN=your-api-token
   ```

3. The `.env` file is automatically loaded and gitignored for security

### Option 2: Direct Script Configuration
Update the ZENDESK_CONFIG object in `zendesk_tickets_scraper.js`:

```javascript
const ZENDESK_CONFIG = {
  subdomain: 'your-subdomain',
  email: 'your-email@domain.com', 
  apiToken: 'your-api-token',
  // ... rest of config
};
```

## Getting Your Credentials

### 1. Subdomain
- Look at your Zendesk URL
- If your Zendesk is at `https://mendi.zendesk.com`, then subdomain = `mendi`

### 2. Email
- Use your Zendesk admin email address

### 3. API Token
- Go to Zendesk Admin Center
- Navigate to **Apps and integrations** > **APIs** > **Zendesk API**
- Enable token access and generate a new token
- Copy the token value

## Security Best Practices

- ✅ Use environment variables (Option 1)
- ✅ Never commit `.env` files to version control
- ✅ Regularly rotate API tokens
- ✅ Use minimum required permissions
- ❌ Don't hardcode credentials in scripts
- ❌ Don't share API tokens in chat/email

## Running the Scraper

```bash
# With environment variables
node zendesk_tickets_scraper.js

# Or with the shell script
./run_zendesk_scraper.sh
```
