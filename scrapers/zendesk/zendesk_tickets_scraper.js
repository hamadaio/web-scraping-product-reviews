/**
 * Zendesk Support Tickets Scraper
 * 
 * This script fetches support tickets from Zendesk API and converts them
 * to a standardized review format for analysis in the dashboard.
 * Treats tickets as "reviews" with satisfaction ratings and comments.
 * 
 * Author: M S Hamada
 * Version: 1.0.0
 * Date: July 28, 2025
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Load environment variables from .env file
try {
  const envPath = path.join(__dirname, '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    envContent.split('\n').forEach(line => {
      const [key, value] = line.split('=');
      if (key && value) {
        process.env[key.trim()] = value.trim();
      }
    });
  }
} catch (error) {
  console.warn('Warning: Could not load .env file:', error.message);
}

// Zendesk API configuration
const ZENDESK_CONFIG = {
  // Load from environment variables for security
  subdomain: process.env.ZENDESK_SUBDOMAIN,
  email: process.env.ZENDESK_EMAIL,
  apiToken: process.env.ZENDESK_API_TOKEN,
  
  // API endpoints
  baseUrl: 'https://{subdomain}.zendesk.com/api/v2',
  endpoints: {
    tickets: '/tickets.json',
    satisfaction_ratings: '/satisfaction_ratings.json',
    users: '/users.json'
  }
};

// Helper function to make Zendesk API requests
function makeZendeskRequest(endpoint, params = {}) {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${ZENDESK_CONFIG.email}/token:${ZENDESK_CONFIG.apiToken}`).toString('base64');
    const baseUrl = ZENDESK_CONFIG.baseUrl.replace('{subdomain}', ZENDESK_CONFIG.subdomain);
    
    // Build query string
    const queryString = Object.keys(params).length > 0 ? 
      '?' + Object.entries(params).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&') : '';
    
    const url = baseUrl + endpoint + queryString;
    
    const options = {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Zendesk-Reviews-Scraper/1.0'
      }
    };

    const req = https.request(url, options, (res) => {
      let data = '';
      
      res.on('data', chunk => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve(jsonData);
        } catch (error) {
          reject(new Error(`Failed to parse JSON: ${error.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.end();
  });
}

// Function to fetch all tickets with pagination
async function fetchAllTickets() {
  console.log('Fetching all tickets from Zendesk...');
  
  let allTickets = [];
  let nextPage = null;
  let pageCount = 0;
  
  try {
    do {
      pageCount++;
      console.log(`  Fetching tickets page ${pageCount}...`);
      
      const params = {
        'sort_by': 'created_at',
        'sort_order': 'desc',
        'per_page': 100 // Maximum per page
      };
      
      if (nextPage) {
        // Use the next_page URL directly
        const response = await makeZendeskRequestFromUrl(nextPage);
        if (response.tickets && response.tickets.length > 0) {
          allTickets = allTickets.concat(response.tickets);
          console.log(`    Page ${pageCount}: ${response.tickets.length} tickets (total: ${allTickets.length})`);
          nextPage = response.next_page;
        } else {
          break;
        }
      } else {
        const response = await makeZendeskRequest(ZENDESK_CONFIG.endpoints.tickets, params);
        if (response.tickets && response.tickets.length > 0) {
          allTickets = allTickets.concat(response.tickets);
          console.log(`    Page ${pageCount}: ${response.tickets.length} tickets (total: ${allTickets.length})`);
          nextPage = response.next_page;
        } else {
          break;
        }
      }
      
      // Rate limiting - Zendesk has a 700 requests per minute limit
      await new Promise(resolve => setTimeout(resolve, 100));
      
    } while (nextPage && pageCount < 200); // Safety limit
    
    console.log(`Total tickets fetched: ${allTickets.length}`);
    return allTickets;
    
  } catch (error) {
    console.error('Error fetching tickets:', error.message);
    return allTickets;
  }
}

// Helper function for paginated requests using full URL
function makeZendeskRequestFromUrl(url) {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${ZENDESK_CONFIG.email}/token:${ZENDESK_CONFIG.apiToken}`).toString('base64');
    
    const options = {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Zendesk-Reviews-Scraper/1.0'
      }
    };

    const req = https.request(url, options, (res) => {
      let data = '';
      
      res.on('data', chunk => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve(jsonData);
        } catch (error) {
          reject(new Error(`Failed to parse JSON: ${error.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.end();
  });
}

// Function to fetch satisfaction ratings
async function fetchSatisfactionRatings() {
  console.log('Fetching satisfaction ratings...');
  
  let allRatings = [];
  let nextPage = null;
  let pageCount = 0;
  
  try {
    do {
      pageCount++;
      console.log(`  Fetching ratings page ${pageCount}...`);
      
      const params = {
        'sort_by': 'created_at',
        'sort_order': 'desc',
        'per_page': 100
      };
      
      if (nextPage) {
        const response = await makeZendeskRequestFromUrl(nextPage);
        if (response.satisfaction_ratings && response.satisfaction_ratings.length > 0) {
          allRatings = allRatings.concat(response.satisfaction_ratings);
          console.log(`    Page ${pageCount}: ${response.satisfaction_ratings.length} ratings (total: ${allRatings.length})`);
          nextPage = response.next_page;
        } else {
          break;
        }
      } else {
        const response = await makeZendeskRequest(ZENDESK_CONFIG.endpoints.satisfaction_ratings, params);
        if (response.satisfaction_ratings && response.satisfaction_ratings.length > 0) {
          allRatings = allRatings.concat(response.satisfaction_ratings);
          console.log(`    Page ${pageCount}: ${response.satisfaction_ratings.length} ratings (total: ${allRatings.length})`);
          nextPage = response.next_page;
        } else {
          break;
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
    } while (nextPage && pageCount < 50);
    
    console.log(`Total satisfaction ratings fetched: ${allRatings.length}`);
    return allRatings;
    
  } catch (error) {
    console.error('Error fetching satisfaction ratings:', error.message);
    return allRatings;
  }
}

// Function to convert ticket priority/status to rating
function ticketToRating(ticket) {
  // Convert ticket attributes to a 1-5 rating scale
  // This is customizable based on your needs
  
  if (ticket.satisfaction_rating && ticket.satisfaction_rating.score) {
    // If there's an actual satisfaction rating, use it
    const score = ticket.satisfaction_rating.score;
    if (score === 'offered') return null;
    if (score === 'unoffered') return null;
    if (score === 'received') return null;
    if (score === 'good') return 5;
    if (score === 'bad') return 1;
  }
  
  // Otherwise, infer from ticket status and priority
  let rating = 3; // Default neutral
  
  // Adjust based on status
  if (ticket.status === 'solved' || ticket.status === 'closed') {
    rating += 1; // Assume solved = positive experience
  } else if (ticket.status === 'open' || ticket.status === 'pending') {
    rating -= 1; // Open tickets might indicate frustration
  }
  
  // Adjust based on priority
  if (ticket.priority === 'urgent' || ticket.priority === 'high') {
    rating -= 1; // High priority = more serious issue
  } else if (ticket.priority === 'low') {
    rating += 1; // Low priority = minor issue
  }
  
  // Clamp between 1 and 5
  return Math.max(1, Math.min(5, rating));
}

// Function to extract meaningful text from ticket
function extractTicketText(ticket) {
  let text = '';
  
  // Use subject as primary text
  if (ticket.subject) {
    text += ticket.subject;
  }
  
  // Add description if available
  if (ticket.description && ticket.description !== ticket.subject) {
    text += text ? '. ' + ticket.description : ticket.description;
  }
  
  // Add tags as context
  if (ticket.tags && ticket.tags.length > 0) {
    text += ` [Tags: ${ticket.tags.join(', ')}]`;
  }
  
  return text || 'No description available';
}

// Main function to convert tickets to review format
function convertTicketsToReviews(tickets, satisfactionRatings) {
  console.log('Converting tickets to review format...');
  
  // Create a map of satisfaction ratings by ticket ID
  const ratingsMap = {};
  satisfactionRatings.forEach(rating => {
    if (rating.ticket_id) {
      ratingsMap[rating.ticket_id] = rating;
    }
  });
  
  const reviews = tickets.map(ticket => {
    // Get satisfaction rating if exists
    const satisfaction = ratingsMap[ticket.id];
    
    // Convert date format
    let date = '';
    if (ticket.created_at) {
      date = new Date(ticket.created_at).toISOString().split('T')[0];
    }
    
    // Determine rating
    let rating = ticketToRating({
      ...ticket,
      satisfaction_rating: satisfaction
    });
    
    // If we have actual satisfaction rating, use that
    if (satisfaction) {
      if (satisfaction.score === 'good') rating = 5;
      else if (satisfaction.score === 'bad') rating = 1;
    }
    
    return {
      id: `zendesk_${ticket.id}_${Math.random().toString(36).substr(2, 9)}`,
      author: ticket.requester_id ? `User ${ticket.requester_id}` : 'Anonymous',
      rating: rating,
      review: extractTicketText(ticket),
      title: ticket.subject || '',
      date: date,
      helpful: 0, // Not applicable for tickets
      platform: 'zendesk',
      ticket_id: ticket.id,
      status: ticket.status,
      priority: ticket.priority,
      satisfaction_score: satisfaction ? satisfaction.score : null,
      tags: ticket.tags || []
    };
  });
  
  console.log(`Converted ${reviews.length} tickets to review format`);
  return reviews;
}

// Main scraping function
async function scrapeZendeskData() {
  console.log('Starting Zendesk data scraping...');
  console.log(`Started at: ${new Date().toISOString()}`);
  
  try {
    // Validate configuration
    if (!ZENDESK_CONFIG.subdomain || !ZENDESK_CONFIG.email || !ZENDESK_CONFIG.apiToken) {
      throw new Error('Missing Zendesk credentials. Please set environment variables or update the script configuration.');
    }
    
    if (ZENDESK_CONFIG.subdomain === 'your-subdomain' || 
        ZENDESK_CONFIG.email === 'your-email@domain.com' || 
        ZENDESK_CONFIG.apiToken === 'your-api-token') {
      throw new Error('Please configure your Zendesk credentials in the script or environment variables');
    }
    
    const startTime = Date.now();
    
    // Fetch tickets and satisfaction ratings in parallel
    const [tickets, satisfactionRatings] = await Promise.all([
      fetchAllTickets(),
      fetchSatisfactionRatings()
    ]);
    
    if (tickets.length === 0) {
      console.log('No tickets found');
      return;
    }
    
    // Convert to review format
    const reviews = convertTicketsToReviews(tickets, satisfactionRatings);
    
    // Generate files
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    
    // CSV format
    const csv = 'Date,User,Rating,Review,Title,Status,Priority,Satisfaction,Tags\n' + 
      reviews.map(r => {
        const date = r.date || '';
        const author = (r.author || '').replace(/"/g, '""');
        const rating = r.rating || '';
        const review = (r.review || '').replace(/"/g, '""');
        const title = (r.title || '').replace(/"/g, '""');
        const status = (r.status || '').replace(/"/g, '""');
        const priority = (r.priority || '').replace(/"/g, '""');
        const satisfaction = (r.satisfaction_score || '').replace(/"/g, '""');
        const tags = (r.tags ? r.tags.join(', ') : '').replace(/"/g, '""');
        
        return `"${date}","${author}","${rating}","${review}","${title}","${status}","${priority}","${satisfaction}","${tags}"`;
      }).join('\n');
    
    // Save CSV
    const csvFilename = `zendesk_tickets_${timestamp}.csv`;
    fs.writeFileSync(csvFilename, csv);
    console.log(`CSV saved: ${csvFilename}`);
    
    // Save JSON (dashboard format)
    const jsonFilename = `zendesk_reviews_${timestamp}.json`;
    fs.writeFileSync(jsonFilename, JSON.stringify(reviews, null, 2));
    console.log(`JSON saved: ${jsonFilename}`);
    
    // Copy to dashboard data directory
    const dashboardJsonPath = '../../dashboard/data/zendesk_reviews.json';
    fs.writeFileSync(dashboardJsonPath, JSON.stringify(reviews, null, 2));
    console.log(`Dashboard JSON saved: ${dashboardJsonPath}`);
    
    // Statistics
    const ratings = reviews.map(r => r.rating).filter(r => r);
    const avgRating = ratings.length > 0 ? ratings.reduce((a, b) => a + b, 0) / ratings.length : 0;
    
    const endTime = Date.now();
    console.log(`\nZENDESK SCRAPING COMPLETE:`);
    console.log(`Total time: ${((endTime - startTime) / 1000 / 60).toFixed(1)} minutes`);
    console.log(`Total tickets: ${tickets.length}`);
    console.log(`Satisfaction ratings: ${satisfactionRatings.length}`);
    console.log(`Reviews generated: ${reviews.length}`);
    console.log(`Average rating: ${avgRating.toFixed(2)}/5`);
    
    // Rating distribution
    console.log(`Rating distribution:`);
    for (let i = 1; i <= 5; i++) {
      const count = ratings.filter(r => r === i).length;
      const percentage = ratings.length > 0 ? ((count / ratings.length) * 100).toFixed(1) : 0;
      console.log(`   ${i} star: ${count} reviews (${percentage}%)`);
    }
    
    // Status distribution
    const statusCount = {};
    reviews.forEach(r => {
      const status = r.status || 'unknown';
      statusCount[status] = (statusCount[status] || 0) + 1;
    });
    
    console.log(`\nTicket status distribution:`);
    Object.entries(statusCount)
      .sort((a, b) => b[1] - a[1])
      .forEach(([status, count]) => {
        const percentage = ((count / reviews.length) * 100).toFixed(1);
        console.log(`   ${status}: ${count} tickets (${percentage}%)`);
      });
    
  } catch (error) {
    console.error('Error during scraping:', error.message);
    console.error('\nSetup instructions:');
    console.error('1. Replace ZENDESK_CONFIG values with your actual Zendesk details');
    console.error('2. Get API token from Zendesk Admin > Channels > API');
    console.error('3. Ensure your Zendesk user has API access permissions');
  }
}

// Run the scraper
if (require.main === module) {
  scrapeZendeskData().catch(console.error);
}

module.exports = {
  scrapeZendeskData,
  ZENDESK_CONFIG
};
