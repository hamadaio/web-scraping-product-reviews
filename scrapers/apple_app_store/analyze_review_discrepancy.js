/**
 * Quick analysis of why scraper finds fewer reviews than App Store Connect
 */

const store = require('app-store-scraper');

async function analyzeReviewDiscrepancy() {
  console.log('🔍 Analyzing App Store review discrepancy...\n');
  
  // Test different sorting methods
  const sortMethods = [
    { name: 'RECENT', value: store.sort.RECENT },
    { name: 'HELPFUL', value: store.sort.HELPFUL },
    { name: 'RATING', value: store.sort.RATING }
  ];
  
  console.log('📊 Testing different sort methods (US only, first page):');
  
  for (const sortMethod of sortMethods) {
    try {
      const reviews = await store.reviews({
        id: '1548944912',
        sort: sortMethod.value,
        page: 1,
        country: 'us'
      });
      
      console.log(`   ${sortMethod.name}: ${reviews.length} reviews on first page`);
      
      if (reviews.length > 0) {
        const ratings = reviews.map(r => r.score).filter(r => r);
        const avgRating = ratings.reduce((a, b) => a + b, 0) / ratings.length;
        console.log(`     Average rating: ${avgRating.toFixed(2)}/5`);
        
        // Check date range
        const dates = reviews.map(r => r.updated || r.date).filter(d => d);
        if (dates.length > 0) {
          const sortedDates = dates.sort();
          console.log(`     Date range: ${sortedDates[0]} to ${sortedDates[sortedDates.length - 1]}`);
        }
      }
    } catch (error) {
      console.log(`   ${sortMethod.name}: Error - ${error.message}`);
    }
    
    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n🌍 Testing a few different countries:');
  const testCountries = ['us', 'gb', 'ca', 'de', 'jp'];
  
  for (const country of testCountries) {
    try {
      const reviews = await store.reviews({
        id: '1548944912',
        sort: store.sort.RECENT,
        page: 1,
        country: country
      });
      
      console.log(`   ${country.toUpperCase()}: ${reviews.length} reviews on first page`);
    } catch (error) {
      console.log(`   ${country.toUpperCase()}: Error - ${error.message}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n💡 Recommendations:');
  console.log('1. Use the GLOBAL scraper to get reviews from multiple countries');
  console.log('2. The app-store-scraper package has known limitations');
  console.log('3. Some reviews may be private or restricted');
  console.log('4. App Store Connect counts all historical reviews, including deleted ones');
  console.log('5. Consider using multiple sort methods to catch different review sets');
}

analyzeReviewDiscrepancy().catch(console.error);
