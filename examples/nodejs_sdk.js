#!/usr/bin/env node

/**
 * PodTranslate Node.js SDK Example
 *
 * Simple client library for interacting with PodTranslate API.
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class PodTranslateClient {
  /**
   * Initialize client.
   *
   * @param {string} apiKey - Your API key
   * @param {string} baseUrl - API base URL
   */
  constructor(apiKey, baseUrl = 'http://localhost:3000/api/v1') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;

    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'X-API-Key': apiKey
      }
    });
  }

  /**
   * Upload audio file and create transcription job.
   *
   * @param {Object} options - Transcription options
   * @returns {Promise<Object>} Job information
   */
  async createTranscription({
    audioFilePath,
    podcastId,
    episodeId,
    sourceLanguage = 'auto',
    targetLanguages = [],
    enableDiarization = true,
    enableTranslation = true,
    enableTts = false
  }) {
    const form = new FormData();
    form.append('file', fs.createReadStream(audioFilePath));
    form.append('podcast_id', podcastId);
    form.append('episode_id', episodeId);
    form.append('source_language', sourceLanguage);
    form.append('target_languages', targetLanguages.join(','));
    form.append('enable_diarization', enableDiarization);
    form.append('enable_translation', enableTranslation);
    form.append('enable_tts', enableTts);

    const response = await axios.post(
      `${this.baseUrl}/transcriptions/upload`,
      form,
      {
        headers: {
          ...form.getHeaders(),
          'X-API-Key': this.apiKey
        }
      }
    );

    return response.data;
  }

  /**
   * Get transcription job status.
   *
   * @param {string} jobId - Job ID
   * @returns {Promise<Object>} Job status
   */
  async getJobStatus(jobId) {
    const response = await this.client.get(`/transcriptions/${jobId}`);
    return response.data;
  }

  /**
   * Wait for job to complete.
   *
   * @param {string} jobId - Job ID
   * @param {number} timeout - Maximum time to wait (ms)
   * @param {number} pollInterval - Time between checks (ms)
   * @returns {Promise<Object>} Final job status
   */
  async waitForCompletion(jobId, timeout = 3600000, pollInterval = 10000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const status = await this.getJobStatus(jobId);

      if (status.status === 'completed') {
        return status;
      } else if (status.status === 'failed') {
        throw new Error(`Job failed: ${status.error}`);
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error(`Job did not complete within ${timeout}ms`);
  }

  /**
   * Generate blog post from transcript.
   *
   * @param {Object} options - Blog generation options
   * @returns {Promise<Object>} Generated blog post
   */
  async generateBlogPost({
    transcript,
    title,
    style = 'informative',
    length = 'medium'
  }) {
    const response = await this.client.post('/ai-tools/generate/blog', {
      transcript,
      title,
      style,
      length
    });

    return response.data;
  }

  /**
   * Generate social media posts.
   *
   * @param {Object} options - Social media options
   * @returns {Promise<Object>} Generated posts
   */
  async generateSocialMedia({ transcript, platforms }) {
    const response = await this.client.post('/ai-tools/generate/social', {
      transcript,
      platforms,
      count: 5
    });

    return response.data;
  }

  /**
   * Get podcast analytics.
   *
   * @param {string} podcastId - Podcast ID
   * @param {string} startDate - Start date (YYYY-MM-DD)
   * @param {string} endDate - End date (YYYY-MM-DD)
   * @returns {Promise<Object>} Analytics data
   */
  async getAnalytics(podcastId, startDate, endDate) {
    const response = await this.client.get(`/analytics/podcasts/${podcastId}`, {
      params: { start_date: startDate, end_date: endDate }
    });

    return response.data;
  }
}

// Example usage
async function main() {
  // Initialize client
  const client = new PodTranslateClient(
    'your-api-key-here',
    'http://localhost:3000/api/v1'
  );

  try {
    // Upload and transcribe
    console.log('📤 Uploading audio file...');
    const job = await client.createTranscription({
      audioFilePath: 'podcast_episode.mp3',
      podcastId: 'my-podcast',
      episodeId: 'episode-001',
      sourceLanguage: 'en',
      targetLanguages: ['es', 'fr', 'de'],
      enableDiarization: true,
      enableTranslation: true
    });

    console.log(`✅ Job created: ${job.job_id}`);

    // Wait for completion
    console.log('⏳ Waiting for transcription to complete...');
    const result = await client.waitForCompletion(job.job_id);

    console.log('✅ Transcription completed!');
    console.log(`   Transcription URL: ${result.transcription_url}`);
    console.log(`   Translations: ${Object.keys(result.translations).join(', ')}`);

    // Generate blog post
    console.log('\n📝 Generating blog post...');
    const blog = await client.generateBlogPost({
      transcript: result.transcript.text,
      title: 'My Awesome Podcast Episode',
      style: 'informative'
    });

    console.log(`✅ Blog post generated (${blog.metadata.word_count} words)`);

    // Generate social media
    console.log('\n📱 Generating social media posts...');
    const social = await client.generateSocialMedia({
      transcript: result.transcript.text,
      platforms: ['twitter', 'linkedin']
    });

    console.log('✅ Social media posts generated:');
    for (const [platform, posts] of Object.entries(social.social_media)) {
      console.log(`   ${platform}: ${posts.length} posts`);
    }

    // Get analytics
    console.log('\n📊 Fetching analytics...');
    const analytics = await client.getAnalytics(
      'my-podcast',
      '2024-01-01',
      '2024-01-31'
    );

    console.log('✅ Analytics retrieved:');
    console.log(`   Total downloads: ${analytics.metrics.downloads.total}`);
    console.log(`   By language:`, analytics.metrics.downloads.by_language);

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Run example
if (require.main === module) {
  main();
}

module.exports = PodTranslateClient;
