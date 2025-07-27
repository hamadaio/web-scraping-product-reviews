/**
 * Enhanced Apple App Store Mendi App Review Scraper
 * 
 * This script attempts to scrape ALL reviews from multiple countries
 * to match the total shown in App Store Connect
 * 
 * Author: M S Hamada
 * Version: 2.0.0
 * Date: July 27, 2025
 */

const store = require('app-store-scraper');
const fs = require('fs');

// ALL countries supported by Apple App Store
const COUNTRIES = [
  // North America
  'us', 'ca', 'mx', 'gt', 'bz', 'sv', 'hn', 'ni', 'cr', 'pa',
  
  // South America
  'ar', 'bo', 'br', 'cl', 'co', 'ec', 'gy', 'py', 'pe', 'sr', 'uy', 've',
  
  // Europe
  'ad', 'al', 'at', 'by', 'be', 'ba', 'bg', 'hr', 'cy', 'cz', 'dk', 'ee', 'fi', 'fr', 
  'de', 'gr', 'hu', 'is', 'ie', 'it', 'lv', 'li', 'lt', 'lu', 'mk', 'mt', 'md', 'mc', 
  'me', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sm', 'rs', 'sk', 'si', 'es', 'se', 'ch', 
  'tr', 'ua', 'gb', 'va',
  
  // Asia Pacific
  'au', 'bn', 'kh', 'cn', 'fj', 'hk', 'in', 'id', 'jp', 'kz', 'kg', 'la', 'mo', 'my', 
  'mv', 'mn', 'mm', 'np', 'nz', 'pk', 'pg', 'ph', 'sg', 'kr', 'lk', 'tw', 'tj', 'th', 
  'tm', 'uz', 'vn',
  
  // Middle East & Africa
  'dz', 'ao', 'bj', 'bw', 'bf', 'cv', 'td', 'eg', 'gq', 'et', 'ga', 'gh', 'gn', 'gw', 
  'ci', 'ke', 'lr', 'ly', 'mg', 'mw', 'ml', 'mr', 'mu', 'ma', 'mz', 'na', 'ne', 'ng', 
  'rw', 'st', 'sn', 'sc', 'sl', 'za', 'sz', 'tz', 'tn', 'ug', 'zm', 'zw',
  
  // Middle East
  'af', 'bh', 'ir', 'iq', 'il', 'jo', 'kw', 'lb', 'om', 'qa', 'sa', 'sy', 'ae', 'ye',
  
  // Caribbean & Others
  'ag', 'bs', 'bb', 'dm', 'do', 'gd', 'jm', 'kn', 'lc', 'vc', 'tt',
  
  // Europe (Additional)
  'az', 'ge', 'am'
];

// Function to scrape reviews from a specific country
async function scrapeCountryReviews(countryCode, maxPages = 20) {
  console.log(`\n🌍 Scraping reviews from ${countryCode.toUpperCase()}...`);
  
  let allReviews = [];
  let pageCount = 0;
  let consecutiveEmptyPages = 0;
  
  try {
    do {
      pageCount++;
      console.log(`  📄 ${countryCode}: Fetching page ${pageCount}...`);
      
      const options = {
        id: '1548944912', // Mendi app ID
        sort: store.sort.RECENT,
        page: pageCount,
        country: countryCode
      };
      
      const reviews = await store.reviews(options);
      
      if (reviews && reviews.length > 0) {
        // Add country info to each review
        const reviewsWithCountry = reviews.map(r => ({
          ...r,
          country: countryCode
        }));
        
        allReviews = allReviews.concat(reviewsWithCountry);
        console.log(`  ✓ ${countryCode}: Page ${pageCount} - ${reviews.length} reviews (country total: ${allReviews.length})`);
        
        consecutiveEmptyPages = 0; // Reset counter
        
        // Shorter delay for faster processing
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Stop if we get very few reviews (likely end of available reviews)
        if (reviews.length < 5) {
          console.log(`  🏁 ${countryCode}: Very few reviews found, likely end of available reviews`);
          break;
        }
      } else {
        consecutiveEmptyPages++;
        console.log(`  ❌ ${countryCode}: No reviews found on page ${pageCount} (empty pages: ${consecutiveEmptyPages})`);
        
        // Stop after 2 consecutive empty pages
        if (consecutiveEmptyPages >= 2) {
          console.log(`  🛑 ${countryCode}: Stopping after ${consecutiveEmptyPages} consecutive empty pages`);
          break;
        }
      }
      
    } while (pageCount < maxPages);
    
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

// Function to remove duplicate reviews (same user + same text + same date)
function removeDuplicates(reviews) {
  const seen = new Set();
  const unique = [];
  
  for (const review of reviews) {
    const key = `${review.userName}_${review.text}_${review.updated}`;
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
  console.log('🚀 Starting WORLDWIDE Apple App Store review scraping for Mendi app...');
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
    
    // Shorter delay between countries for faster processing
    if (i < COUNTRIES.length - 1) { // Don't wait after the last country
      console.log('⏳ Waiting 1 second before next country...');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Progress checkpoint every 20 countries
    if (totalCountriesProcessed % 20 === 0) {
      console.log(`\n� CHECKPOINT: Processed ${totalCountriesProcessed}/${COUNTRIES.length} countries`);
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
  uniqueReviews.sort((a, b) => new Date(b.updated || b.date) - new Date(a.updated || a.date));
  
  // Create enhanced CSV with country info
  const csv = 'Date,Country,User Name,Score,Title,Review Text,Version,Helpful Count\n' + 
    uniqueReviews.map(r => {
      let date = '';
      const dateField = r.updated || r.date;
      if (dateField) {
        if (dateField instanceof Date) {
          date = dateField.toISOString().split('T')[0];
        } else if (typeof dateField === 'string') {
          date = dateField;
        } else {
          date = String(dateField);
        }
      }
      
      const country = (r.country || 'unknown').replace(/"/g, '""');
      const userName = (r.userName || '').replace(/"/g, '""');
      const score = r.score || '';
      const title = (r.title || '').replace(/"/g, '""');
      const text = (r.text || '').replace(/"/g, '""');
      const version = (r.version || '').replace(/"/g, '""');
      const helpfulCount = r.helpfulCount || '';
      
      return `"${date}","${country}","${userName}","${score}","${title}","${text}","${version}","${helpfulCount}"`;
    }).join('\n');
  
  // Create enhanced JSON with country info
  const jsonData = uniqueReviews.map(r => {
    let date = '';
    const dateField = r.updated || r.date;
    if (dateField) {
      if (dateField instanceof Date) {
        date = dateField.toISOString().split('T')[0];
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
      platform: 'app_store',
      country: r.country || 'unknown'
    };
  });
  
  // Save files with timestamp
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  const csvFilename = `mendi_apple-app-store_WORLDWIDE_reviews_${timestamp}.csv`;
  const jsonFilename = `mendi_apple-app-store_WORLDWIDE_reviews_${timestamp}.json`;
  
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
  
  // Version distribution
  const versions = uniqueReviews.map(r => r.version).filter(v => v);
  if (versions.length > 0) {
    const versionCount = {};
    versions.forEach(v => versionCount[v] = (versionCount[v] || 0) + 1);
    console.log(`\n📱 Top app versions in reviews:`);
    Object.entries(versionCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .forEach(([version, count]) => {
        console.log(`   v${version}: ${count} reviews`);
      });
  }
  
  // Compare with App Store Connect
  console.log(`\n🔍 COMPARISON WITH APP STORE CONNECT:`);
  console.log(`   App Store Connect: 285 reviews`);
  console.log(`   Scraper found: ${uniqueReviews.length} reviews`);
  console.log(`   Difference: ${285 - uniqueReviews.length} reviews`);
  console.log(`   Coverage: ${((uniqueReviews.length / 285) * 100).toFixed(1)}%`);
  
  if (uniqueReviews.length < 285) {
    console.log(`\n💡 Possible reasons for missing reviews:`);
    console.log(`   • Some reviews may be from countries not included in scraping`);
    console.log(`   • Private or restricted reviews not accessible via API`);
    console.log(`   • Rate limiting preventing access to all reviews`);
    console.log(`   • Reviews from very old versions or deleted reviews still counted in Connect`);
  }
}

// Run the enhanced global scraper
scrapeAllReviewsGlobal().catch(console.error);
