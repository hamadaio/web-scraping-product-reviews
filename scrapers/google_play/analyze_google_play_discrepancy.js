/**
 * Quick analysis of Google Play review discrepancy
 */

const gplay = require('google-play-scraper').default || require('google-play-scraper');

async function analyzeGooglePlayDiscrepancy() {
  console.log('🔍 Analyzing Google Play review discrepancy...\n');
  
  // Test different sorting methods
  const sortMethods = [
    { name: 'NEWEST', value: gplay.sort?.NEWEST || 'newest' },
    { name: 'RATING', value: gplay.sort?.RATING || 'rating' },
    { name: 'HELPFULNESS', value: gplay.sort?.HELPFULNESS || 'helpfulness' }
  ];
  
  console.log('📊 Testing different sort methods (US only, first batch):');
  
  for (const sortMethod of sortMethods) {
    try {
      const result = await gplay.reviews({
        appId: 'com.mendi.app',
        sort: sortMethod.value,
        num: 100,
        throttle: 10,
        country: 'us'
      });
      
      const reviews = Array.isArray(result) ? result : (result.data || result);
      console.log(`   ${sortMethod.name}: ${reviews.length} reviews in first batch`);
      
      if (reviews.length > 0) {
        const ratings = reviews.map(r => r.score).filter(r => r);
        const avgRating = ratings.reduce((a, b) => a + b, 0) / ratings.length;
        console.log(`     Average rating: ${avgRating.toFixed(2)}/5`);
        
        // Check date range
        const dates = reviews.map(r => r.date).filter(d => d);
        if (dates.length > 0) {
          const sortedDates = dates.sort();
          console.log(`     Date range: ${sortedDates[0]} to ${sortedDates[sortedDates.length - 1]}`);
        }
      }
    } catch (error) {
      console.log(`   ${sortMethod.name}: Error - ${error.message}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log('\n🌍 Testing different countries:');
  const testCountries = ['us', 'gb', 'ca', 'de', 'jp', 'in', 'br'];
  
  for (const country of testCountries) {
    try {
      const result = await gplay.reviews({
        appId: 'com.mendi.app',
        sort: gplay.sort?.NEWEST || 'newest',
        num: 50,
        throttle: 10,
        country: country
      });
      
      const reviews = Array.isArray(result) ? result : (result.data || result);
      console.log(`   ${country.toUpperCase()}: ${reviews.length} reviews in first batch`);
      
      if (reviews.length > 0) {
        const hasToken = result.nextPaginationToken ? 'Has more pages' : 'No more pages';
        console.log(`     ${hasToken}`);
      }
    } catch (error) {
      console.log(`   ${country.toUpperCase()}: Error - ${error.message}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
  
  console.log('\n💡 Recommendations for getting closer to 203 reviews:');
  console.log('1. Use the WORLDWIDE scraper to get reviews from multiple countries');
  console.log('2. Try different sorting methods (newest, rating, helpfulness)');
  console.log('3. Some reviews might be in local languages');
  console.log('4. Google Play Console includes reviews that may not be publicly accessible');
  console.log('5. Consider that some countries might have region-specific reviews');
}

analyzeGooglePlayDiscrepancy().catch(console.error);
