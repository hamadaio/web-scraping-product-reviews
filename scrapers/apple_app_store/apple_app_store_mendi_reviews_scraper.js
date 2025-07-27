/**
 * Apple App Store Mendi App Review Scraper
 * 
 * This script scrapes ALL reviews from the Mendi app on Apple App Store
 * and saves them to a CSV file with date, username, score, and review text.
 * Uses pagination to fetch all available reviews in batches.
 * 
 * Author: M S Hamada
 * Version: 1.0.0
 * Date: July 27, 2025
 */

const store = require('app-store-scraper');
const fs = require('fs');

// --- func to scrape all reviews with pagination
async function scrapeAllReviews() {
  console.log('starting to scrape all apple app store reviews for Mendi app...');
  
  let allReviews = [];
  let pageCount = 0;
  const batchSize = 500; // --- apple app store typically allows larger batches
  
  try {
    do {
      pageCount++;
      console.log(`fetching batch ${pageCount}...`);
      
      const options = {
        id: '1548944912', // --- Mendi app ID on App Store
        sort: store.sort.RECENT,
        page: pageCount,
        country: 'us' // --- can be changed to other countries like 'gb', 'ca', etc.
      };
      
      const reviews = await store.reviews(options);
      
      if (reviews && reviews.length > 0) {
        allReviews = allReviews.concat(reviews);
        console.log(`Batch ${pageCount}: found ${reviews.length} reviews (total so far: ${allReviews.length})`);
        
        // --- debug: check what the date field looks like
        if (pageCount === 1 && reviews[0]) {
          console.log('Debug - First review updated field:', reviews[0].updated, 'Type:', typeof reviews[0].updated);
          console.log('Debug - First review keys:', Object.keys(reviews[0]));
        }
        
        // --- add delay between requests to avoid rate limits
        console.log('waiting 2 seconds before next batch...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // --- if we get fewer reviews than expected, we might be near the end
        if (reviews.length < 50) {
          console.log('received fewer reviews, likely approaching end of available reviews');
        }
      } else {
        console.log('no more reviews found');
        break;
      }
      
    } while (pageCount < 200); // --- safety limit of 200 pages (App Store typically has fewer pages)
    
    console.log(`\nscraping complete... found ${allReviews.length} total apple app store reviews`);
    
    // --- create CSV with all reviews
    const csv = 'Date,User Name,Score,Title,Review Text,Version,Helpful Count\n' + 
      allReviews.map(r => {
        // --- handle date formatting properly (Apple App Store uses 'updated' field)
        let date = '';
        const dateField = r.updated || r.date;
        if (dateField) {
          if (dateField instanceof Date) {
            date = dateField.toISOString().split('T')[0]; // YYYY-MM-DD format
          } else if (typeof dateField === 'string') {
            date = dateField;
          } else {
            date = String(dateField);
          }
        }
        
        const userName = (r.userName || '').replace(/"/g, '""');
        const score = r.score || '';
        const title = (r.title || '').replace(/"/g, '""');
        const text = (r.text || '').replace(/"/g, '""');
        const version = (r.version || '').replace(/"/g, '""');
        const helpfulCount = r.helpfulCount || '';
        
        return `"${date}","${userName}","${score}","${title}","${text}","${version}","${helpfulCount}"`;
      }).join('\n');
    
    // --- save to files with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const csvFilename = `mendi_apple-app-store_reviews_${timestamp}.csv`;
    const jsonFilename = `mendi_apple-app-store_reviews_${timestamp}.json`;
    
    // --- save CSV file
    fs.writeFileSync(csvFilename, csv);
    console.log(`CSV reviews saved --> ${csvFilename}`);
    console.log(`CSV File size: ${(fs.statSync(csvFilename).size / 1024 / 1024).toFixed(2)} MB`);
    
    // --- save JSON file
    const jsonData = allReviews.map(r => {
      // --- handle date formatting properly for JSON
      let date = '';
      const dateField = r.updated || r.date;
      if (dateField) {
        if (dateField instanceof Date) {
          date = dateField.toISOString().split('T')[0]; // YYYY-MM-DD format
        } else if (typeof dateField === 'string') {
          date = dateField;
        } else {
          date = String(dateField);
        }
      }
      
      return {
        id: `app_store_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        author: r.userName || 'Anonymous',
        rating: r.score || null,
        review: r.text || '',
        title: r.title || '',
        date: date,
        helpful: r.helpfulCount || 0,
        version: r.version || '',
        platform: 'app_store'
      };
    });
    
    fs.writeFileSync(jsonFilename, JSON.stringify(jsonData, null, 2));
    console.log(`JSON reviews saved --> ${jsonFilename}`);
    console.log(`JSON File size: ${(fs.statSync(jsonFilename).size / 1024 / 1024).toFixed(2)} MB`);
    
    // --- print some bulk stats
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
    
    // --- show version distribution if available
    const versions = allReviews.map(r => r.version).filter(v => v);
    if (versions.length > 0) {
      const versionCount = {};
      versions.forEach(v => versionCount[v] = (versionCount[v] || 0) + 1);
      console.log(`\ntop app versions in reviews:`);
      Object.entries(versionCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .forEach(([version, count]) => {
          console.log(`  v${version}: ${count} reviews`);
        });
    }
    
  } catch (error) {
    console.error('error scraping reviews:', error);
    console.error('make sure you have the correct app ID and the app-store-scraper package installed');
  }
}

// --- run apple app store scraper
scrapeAllReviews();
