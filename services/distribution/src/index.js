/**
 * Distribution Service - Platform distribution and RSS management
 */

const express = require('express');
const Queue = require('bull');
require('dotenv').config();

const logger = require('./utils/logger');
const SpotifyService = require('./platforms/spotify');
const ApplePodcastsService = require('./platforms/apple');
const GooglePodcastsService = require('./platforms/google');
const YouTubeService = require('./platforms/youtube');
const RSSService = require('./rss/rss-service');

const app = express();
const PORT = process.env.DISTRIBUTION_PORT || 3002;

// Middleware
app.use(express.json());

// Initialize services
const spotifyService = new SpotifyService();
const appleService = new ApplePodcastsService();
const googleService = new GooglePodcastsService();
const youtubeService = new YouTubeService();
const rssService = new RSSService();

// Initialize Bull queue for distribution jobs
const distributionQueue = new Queue('distribution', process.env.REDIS_URL || 'redis://localhost:6379');

// Queue processor
distributionQueue.process(async (job) => {
  const { platform, episodeData, language } = job.data;

  logger.info(`Processing distribution job for ${platform}`, { jobId: job.id });

  try {
    let result;

    switch (platform) {
      case 'spotify':
        result = await spotifyService.publishEpisode(episodeData, language);
        break;
      case 'apple':
        result = await appleService.publishEpisode(episodeData, language);
        break;
      case 'google':
        result = await googleService.publishEpisode(episodeData, language);
        break;
      case 'youtube':
        result = await youtubeService.publishEpisode(episodeData, language);
        break;
      default:
        throw new Error(`Unknown platform: ${platform}`);
    }

    logger.info(`Distribution completed for ${platform}`, { result });
    return result;

  } catch (error) {
    logger.error(`Distribution failed for ${platform}`, { error: error.message });
    throw error;
  }
});

// Routes
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'distribution',
    timestamp: new Date().toISOString()
  });
});

/**
 * Distribute episode to platforms
 */
app.post('/distribute', async (req, res) => {
  try {
    const { episodeId, platforms, languages } = req.body;

    if (!episodeId || !platforms || !languages) {
      return res.status(400).json({
        error: 'Missing required fields: episodeId, platforms, languages'
      });
    }

    const jobs = [];

    for (const platform of platforms) {
      for (const language of languages) {
        const job = await distributionQueue.add({
          episodeId,
          platform,
          language,
          episodeData: req.body.episodeData
        });

        jobs.push({
          platform,
          language,
          jobId: job.id
        });
      }
    }

    res.json({
      message: 'Distribution jobs created',
      jobs
    });

  } catch (error) {
    logger.error('Error creating distribution jobs', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get distribution job status
 */
app.get('/jobs/:jobId', async (req, res) => {
  try {
    const job = await distributionQueue.getJob(req.params.jobId);

    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }

    const state = await job.getState();
    const progress = job.progress();

    res.json({
      jobId: job.id,
      state,
      progress,
      data: job.data,
      result: job.returnvalue,
      failedReason: job.failedReason
    });

  } catch (error) {
    logger.error('Error getting job status', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

/**
 * Generate RSS feed
 */
app.post('/rss/generate', async (req, res) => {
  try {
    const { podcastId, language } = req.body;

    const feedUrl = await rssService.generateFeed(podcastId, language);

    res.json({
      message: 'RSS feed generated',
      feedUrl
    });

  } catch (error) {
    logger.error('Error generating RSS feed', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get RSS feed
 */
app.get('/rss/:podcastId/:language', async (req, res) => {
  try {
    const { podcastId, language } = req.params;

    const feed = await rssService.getFeed(podcastId, language);

    res.set('Content-Type', 'application/rss+xml');
    res.send(feed);

  } catch (error) {
    logger.error('Error getting RSS feed', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

/**
 * Sync episode to all configured platforms
 */
app.post('/sync', async (req, res) => {
  try {
    const { episodeId } = req.body;

    // Get episode data from database
    // This would fetch from your database
    const episodeData = req.body.episodeData;

    // Determine which platforms to sync to
    const platforms = ['spotify', 'apple', 'google', 'youtube'];
    const languages = episodeData.availableLanguages || ['en'];

    const jobs = [];

    for (const platform of platforms) {
      for (const language of languages) {
        const job = await distributionQueue.add({
          episodeId,
          platform,
          language,
          episodeData
        });

        jobs.push({
          platform,
          language,
          jobId: job.id
        });
      }
    }

    res.json({
      message: 'Sync jobs created',
      jobs
    });

  } catch (error) {
    logger.error('Error creating sync jobs', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  logger.info(`Distribution service running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM signal received: closing distribution service');
  await distributionQueue.close();
  process.exit(0);
});

module.exports = app;
