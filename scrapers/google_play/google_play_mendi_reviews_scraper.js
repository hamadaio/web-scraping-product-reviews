/**
 * Google Play Mendi App Review Scraper
 * 
 * This script scrapes ALL reviews from the Mendi app on Google Play Store
 * and saves them to a CSV file with date, username, score, and review text.
 * Uses pagination to fetch all available reviews in batches.
 * 
 * Author: M S Hamada
 * Version: 1.0.0
 * Date: July 27, 2025
 */

const gplay = require('google-play-scraper').default || require('google-play-scraper');
const fs = require('fs');

// Function to scrape all reviews with pagination
async function scrapeAllReviews() {
  console.log('starting to scrape all google play reviews for Mendi app...');
  
  let allReviews = [];
  let nextPaginationToken = null;
  let pageCount = 0;
  const batchSize = 200; // Fetch 200 reviews per batch
  
  try {
    do {
      pageCount++;
      console.log(`fetching batch ${pageCount}...`);
      
      const options = {
        appId: 'com.mendi.app',
        sort: gplay.sort?.NEWEST || 'newest',
        num: batchSize,
        throttle: 10
      };
      
      // Add pagination token if we have one
      if (nextPaginationToken) {
        options.nextPaginationToken = nextPaginationToken;
      }
      
      const result = await gplay.reviews(options);
      const reviews = Array.isArray(result) ? result : (result.data || result);
      
      if (reviews && reviews.length > 0) {
        allReviews = allReviews.concat(reviews);
        console.log(`Batch ${pageCount}: found ${reviews.length} reviews (total so far: ${allReviews.length})`);
        
        // Check if there's a next page
        nextPaginationToken = result.nextPaginationToken;
        
        // Add delay between requests to be respectful to the API
        if (nextPaginationToken) {
          console.log('waiting 2 seconds before next batch...');
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      } else {
        console.log('no more reviews found');
        break;
      }
      
    } while (nextPaginationToken && pageCount < 100); // Safety limit of 100 pages
    
    console.log(`\nScraping complete! Found ${allReviews.length} total reviews.`);
    
    // Create CSV with all reviews
    const csv = 'Date,User Name,Score,Review Text,Helpful Count,Reply Date,Reply Text\n' + 
      allReviews.map(r => {
        const date = r.date || '';
        const userName = (r.userName || '').replace(/"/g, '""');
        const score = r.score || '';
        const text = (r.text || '').replace(/"/g, '""');
        const helpfulCount = r.helpfulCount || '';
        const replyDate = r.replyDate || '';
        const replyText = (r.replyText || '').replace(/"/g, '""');
        
        return `"${date}","${userName}","${score}","${text}","${helpfulCount}","${replyDate}","${replyText}"`;
      }).join('\n');
    
    // Save to file with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = `mendi_all_reviews_${timestamp}.csv`;
    
    fs.writeFileSync(filename, csv);
    console.log(`All reviews saved to: ${filename}`);
    console.log(`File size: ${(fs.statSync(filename).size / 1024 / 1024).toFixed(2)} MB`);
    
    // Show some statistics
    const ratings = allReviews.map(r => r.score).filter(s => s);
    const avgRating = ratings.reduce((a, b) => a + b, 0) / ratings.length;
    console.log(`\nstats:`);
    console.log(`total reviews: ${allReviews.length}`);
    console.log(`average rating: ${avgRating.toFixed(2)}/5`);
    console.log(`rating dist:`);
    for (let i = 1; i <= 5; i++) {
      const count = ratings.filter(r => r === i).length;
      const percentage = ((count / ratings.length) * 100).toFixed(1);
      console.log(`  ${i} star: ${count} reviews (${percentage}%)`);
    }
    
  } catch (error) {
    console.error('error scraping reviews:', error);
  }
}

// Run the scraper
scrapeAllReviews();