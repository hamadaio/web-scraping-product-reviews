/**
 * Enhanced Google Play Mendi App Review Scraper - WORLDWIDE
 * 
 * This script scrapes ALL reviews from multiple countries
 * to match the total shown in Google Play Console
 * 
 * Author: M S Hamada
 * Version: 2.0.0
 * Date: July 27, 2025
 */

const gplay = require('google-play-scraper').default || require('google-play-scraper');
const fs = require('fs');

// Major countries to scrape from (Google Play supported regions)
const COUNTRIES = [
  // Major markets
  'us', 'gb', 'ca', 'au', 'de', 'fr', 'it', 'es', 'nl', 'jp', 'kr', 'br', 'mx', 'in', 'ru',
  
  // Europe
  'at', 'be', 'bg', 'hr', 'cy', 'cz', 'dk', 'ee', 'fi', 'gr', 'hu', 'ie', 'lv', 'lt', 'lu',
  'mt', 'pl', 'pt', 'ro', 'sk', 'si', 'se', 'no', 'ch', 'is',
  
  // Asia Pacific
  'cn', 'hk', 'tw', 'sg', 'my', 'th', 'ph', 'id', 'vn', 'nz',
  
  // Americas
  'ar', 'cl', 'co', 'pe', 'uy', 've', 'cr', 'pa', 'gt', 'sv', 'hn', 'ni',
  
  // Middle East & Africa
  'ae', 'sa', 'il', 'tr', 'za', 'eg', 'ma', 'ng', 'ke', 'gh',
  
  // Others
  'pk', 'bd', 'lk', 'np'
];

// Function to scrape reviews from a specific country
async function scrapeCountryReviews(countryCode, maxBatches = 10) {
  console.log(`\n🌍 Scraping Google Play reviews from ${countryCode.toUpperCase()}...`);
  
  let allReviews = [];
  let nextPaginationToken = null;
  let batchCount = 0;
  const batchSize = 150; // Smaller batches for better reliability
  
  try {
    do {
      batchCount++;
      console.log(`  📄 ${countryCode}: Fetching batch ${batchCount}...`);
      
      const options = {
        appId: 'com.mendi.app',
        sort: gplay.sort?.NEWEST || 'newest',
        num: batchSize,
        throttle: 10,
        country: countryCode,
        lang: 'en' // Try English first, then local language
      };
      
      if (nextPaginationToken) {
        options.nextPaginationToken = nextPaginationToken;
      }
      
      const result = await gplay.reviews(options);
      const reviews = Array.isArray(result) ? result : (result.data || result);
      
      if (reviews && reviews.length > 0) {
        // Add country info to each review
        const reviewsWithCountry = reviews.map(r => ({
          ...r,
          country: countryCode
        }));
        
        allReviews = allReviews.concat(reviewsWithCountry);
        console.log(`  ✓ ${countryCode}: Batch ${batchCount} - ${reviews.length} reviews (country total: ${allReviews.length})`);
        
        nextPaginationToken = result.nextPaginationToken;
        
        // Shorter delay for faster processing
        if (nextPaginationToken) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // Stop if we get very few reviews
        if (reviews.length < 10) {
          console.log(`  🏁 ${countryCode}: Few reviews found, likely end of available reviews`);
          break;
        }
      } else {
        console.log(`  ❌ ${countryCode}: No reviews found`);
        break;
      }
      
    } while (nextPaginationToken && batchCount < maxBatches);
    
    if (allReviews.length > 0) {
      console.log(`✅ ${countryCode} complete: ${allReviews.length} reviews found`);
    } else {
      console.log(`📭 ${countryCode}: No reviews found in this country`);
    }
    return allReviews;
    
  } catch (error) {
    console.error(`❌ Error scraping ${countryCode}:`, error.message);
    return allReviews;
  }
}

// Function to remove duplicate reviews
function removeDuplicates(reviews) {
  const seen = new Set();
  const unique = [];
  
  for (const review of reviews) {
    // Create unique key based on userName + text + date
    const key = `${review.userName}_${review.text}_${review.date}`;
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(review);
    }
  }
  
  console.log(`🔄 Removed ${reviews.length - unique.length} duplicate reviews`);
  return unique;
}

// Main scraping function
async function scrapeAllReviewsGlobal() {
  const startTime = Date.now();
  console.log('🚀 Starting WORLDWIDE Google Play review scraping for Mendi app...');
  console.log(`🌍 Will scrape from ${COUNTRIES.length} countries worldwide!`);
  console.log(`📅 Started at: ${new Date().toISOString()}`);
  
  let allGlobalReviews = [];
  let countriesWithReviews = 0;
  let totalCountriesProcessed = 0;
  
  // Scrape from each country
  for (let i = 0; i < COUNTRIES.length; i++) {
    const country = COUNTRIES[i];
    totalCountriesProcessed++;
    
    console.log(`\n🌐 Progress: ${totalCountriesProcessed}/${COUNTRIES.length} countries (${((totalCountriesProcessed/COUNTRIES.length)*100).toFixed(1)}%)`);
    
    const countryReviews = await scrapeCountryReviews(country);
    
    if (countryReviews.length > 0) {
      allGlobalReviews = allGlobalReviews.concat(countryReviews);
      countriesWithReviews++;
      console.log(`📊 Running total: ${allGlobalReviews.length} reviews from ${countriesWithReviews} countries`);
    }
    
    // Delay between countries
    if (i < COUNTRIES.length - 1) {
      console.log('⏳ Waiting 1.5 seconds before next country...');
      await new Promise(resolve => setTimeout(resolve, 1500));
    }
    
    // Progress checkpoint every 15 countries
    if (totalCountriesProcessed % 15 === 0) {
      console.log(`\n🏁 CHECKPOINT: Processed ${totalCountriesProcessed}/${COUNTRIES.length} countries`);
      console.log(`📈 Current totals: ${allGlobalReviews.length} reviews from ${countriesWithReviews} countries`);
      console.log(`⏰ Time elapsed: ${((Date.now() - startTime) / 1000 / 60).toFixed(1)} minutes`);
    }
  }
  
  const endTime = Date.now();
  console.log(`\n🌍 WORLDWIDE scraping complete!`);
  console.log(`⏰ Total time: ${((endTime - startTime) / 1000 / 60).toFixed(1)} minutes`);
  console.log(`📊 Raw total: ${allGlobalReviews.length} reviews from ${countriesWithReviews}/${COUNTRIES.length} countries`);
  
  // Remove duplicates
  const uniqueReviews = removeDuplicates(allGlobalReviews);
  console.log(`🎯 Final unique reviews: ${uniqueReviews.length}`);
  
  // Sort by date (most recent first)
  uniqueReviews.sort((a, b) => new Date(b.date) - new Date(a.date));
  
  // Create enhanced CSV with country info
  const csv = 'Date,Country,User Name,Score,Review Text,Helpful Count,Reply Date,Reply Text\n' + 
    uniqueReviews.map(r => {
      const date = r.date || '';
      const country = (r.country || 'unknown').replace(/"/g, '""');
      const userName = (r.userName || '').replace(/"/g, '""');
      const score = r.score || '';
      const text = (r.text || '').replace(/"/g, '""');
      const helpfulCount = r.helpfulCount || '';
      const replyDate = r.replyDate || '';
      const replyText = (r.replyText || '').replace(/"/g, '""');
      
      return `"${date}","${country}","${userName}","${score}","${text}","${helpfulCount}","${replyDate}","${replyText}"`;
    }).join('\n');
  
  // Create enhanced JSON with country info
  const jsonData = uniqueReviews.map(r => ({
    id: `google_play_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    author: r.userName || 'Anonymous',
    rating: r.score || null,
    review: r.text || '',
    date: r.date || '',
    helpful: r.helpfulCount || 0,
    reply_date: r.replyDate || '',
    reply_text: r.replyText || '',
    platform: 'google_play',
    country: r.country || 'unknown'
  }));
  
  // Save files with timestamp
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  const csvFilename = `mendi_google-play_WORLDWIDE_reviews_${timestamp}.csv`;
  const jsonFilename = `mendi_google-play_WORLDWIDE_reviews_${timestamp}.json`;
  
  fs.writeFileSync(csvFilename, csv);
  console.log(`💾 Worldwide CSV saved: ${csvFilename}`);
  console.log(`📏 CSV size: ${(fs.statSync(csvFilename).size / 1024 / 1024).toFixed(2)} MB`);
  
  fs.writeFileSync(jsonFilename, JSON.stringify(jsonData, null, 2));
  console.log(`💾 Worldwide JSON saved: ${jsonFilename}`);
  console.log(`📏 JSON size: ${(fs.statSync(jsonFilename).size / 1024 / 1024).toFixed(2)} MB`);
  
  // Detailed statistics
  const ratings = uniqueReviews.map(r => r.score).filter(s => s);
  const avgRating = ratings.reduce((a, b) => a + b, 0) / ratings.length;
  
  console.log(`\n📊 FINAL WORLDWIDE STATISTICS:`);
  console.log(`🌍 Total unique reviews: ${uniqueReviews.length}`);
  console.log(`🏪 Countries with reviews: ${countriesWithReviews}/${COUNTRIES.length}`);
  console.log(`⭐ Average rating: ${avgRating.toFixed(2)}/5`);
  console.log(`📈 Rating distribution:`);
  for (let i = 1; i <= 5; i++) {
    const count = ratings.filter(r => r === i).length;
    const percentage = ((count / ratings.length) * 100).toFixed(1);
    console.log(`   ${i} ⭐: ${count} reviews (${percentage}%)`);
  }
  
  // Country distribution
  const countryCount = {};
  uniqueReviews.forEach(r => {
    const country = r.country || 'unknown';
    countryCount[country] = (countryCount[country] || 0) + 1;
  });
  
  console.log(`\n🌍 Top countries by review count:`);
  Object.entries(countryCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15) // Show top 15 countries
    .forEach(([country, count]) => {
      const percentage = ((count / uniqueReviews.length) * 100).toFixed(1);
      console.log(`   ${country.toUpperCase()}: ${count} reviews (${percentage}%)`);
    });
  
  // Compare with Google Play Console
  console.log(`\n🔍 COMPARISON WITH GOOGLE PLAY CONSOLE:`);
  console.log(`   Google Play Console: 203 reviews`);
  console.log(`   Scraper found: ${uniqueReviews.length} reviews`);
  console.log(`   Difference: ${203 - uniqueReviews.length} reviews`);
  console.log(`   Coverage: ${((uniqueReviews.length / 203) * 100).toFixed(1)}%`);
  
  if (uniqueReviews.length < 203) {
    console.log(`\n💡 Possible reasons for missing reviews:`);
    console.log(`   • Some reviews may be from countries not included in scraping`);
    console.log(`   • Private or restricted reviews not accessible via API`);
    console.log(`   • Rate limiting preventing access to all reviews`);
    console.log(`   • Reviews in local languages that aren't being captured`);
    console.log(`   • Very recent reviews that haven't propagated to all regions`);
  }
}

// Run the enhanced global scraper
scrapeAllReviewsGlobal().catch(console.error);
