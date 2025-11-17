/**
 * RSS Feed Management Service
 */

const RSS = require('rss');
const fs = require('fs').promises;
const path = require('path');
const logger = require('../utils/logger');

class RSSService {
  constructor() {
    this.feedsDir = process.env.RSS_FEEDS_DIR || './feeds';
    this.baseUrl = process.env.RSS_BASE_URL || 'http://localhost:3002/rss';
  }

  /**
   * Generate RSS feed for a podcast in a specific language
   */
  async generateFeed(podcastId, language, episodes = []) {
    try {
      logger.info('Generating RSS feed', { podcastId, language });

      // Fetch podcast data (in production, this would come from database)
      const podcastData = await this.getPodcastData(podcastId, language);

      // Create RSS feed
      const feed = new RSS({
        title: podcastData.title,
        description: podcastData.description,
        feed_url: `${this.baseUrl}/${podcastId}/${language}`,
        site_url: podcastData.websiteUrl,
        image_url: podcastData.coverImageUrl,
        language: language,
        pubDate: new Date(),
        ttl: 60,
        custom_namespaces: {
          'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
          'podcast': 'https://podcastindex.org/namespace/1.0',
          'content': 'http://purl.org/rss/1.0/modules/content/'
        },
        custom_elements: [
          { 'itunes:author': podcastData.author },
          { 'itunes:summary': podcastData.description },
          { 'itunes:owner': [
            { 'itunes:name': podcastData.author },
            { 'itunes:email': podcastData.email }
          ]},
          { 'itunes:explicit': podcastData.explicit ? 'yes' : 'no' },
          { 'itunes:category': [
            { _attr: { text: podcastData.category } }
          ]},
          { 'itunes:image': [
            { _attr: { href: podcastData.coverImageUrl } }
          ]},
          { 'language': language }
        ]
      });

      // Add episodes
      for (const episode of episodes) {
        feed.item({
          title: episode.title,
          description: episode.description,
          url: episode.url,
          guid: episode.id,
          date: episode.publishedAt,
          enclosure: {
            url: episode.audioUrl,
            type: 'audio/mpeg',
            size: episode.audioSize || 0
          },
          custom_elements: [
            { 'itunes:title': episode.title },
            { 'itunes:summary': episode.description },
            { 'itunes:duration': this.formatDuration(episode.durationSeconds) },
            { 'itunes:explicit': episode.explicit ? 'yes' : 'no' },
            { 'itunes:episodeType': episode.type || 'full' },
            { 'itunes:season': episode.seasonNumber },
            { 'itunes:episode': episode.episodeNumber },
            // Podcast namespace 2.0 - Transcripts
            { 'podcast:transcript': [
              {
                _attr: {
                  url: episode.transcriptUrl,
                  type: 'application/json',
                  language: language
                }
              }
            ]},
            // Podcast namespace 2.0 - Chapters
            ...(episode.chaptersUrl ? [{
              'podcast:chapters': [
                {
                  _attr: {
                    url: episode.chaptersUrl,
                    type: 'application/json'
                  }
                }
              ]
            }] : [])
          ]
        });
      }

      const xml = feed.xml({ indent: true });

      // Save feed to file
      await this.saveFeed(podcastId, language, xml);

      logger.info('RSS feed generated successfully', { podcastId, language });

      return `${this.baseUrl}/${podcastId}/${language}`;

    } catch (error) {
      logger.error('Failed to generate RSS feed', { error: error.message });
      throw error;
    }
  }

  /**
   * Get feed XML
   */
  async getFeed(podcastId, language) {
    try {
      const feedPath = path.join(this.feedsDir, podcastId, `${language}.xml`);
      const xml = await fs.readFile(feedPath, 'utf-8');
      return xml;
    } catch (error) {
      logger.error('Failed to get RSS feed', { error: error.message });
      throw error;
    }
  }

  /**
   * Save feed to file
   */
  async saveFeed(podcastId, language, xml) {
    try {
      const feedDir = path.join(this.feedsDir, podcastId);
      await fs.mkdir(feedDir, { recursive: true });

      const feedPath = path.join(feedDir, `${language}.xml`);
      await fs.writeFile(feedPath, xml, 'utf-8');

      logger.info('Feed saved', { feedPath });
    } catch (error) {
      logger.error('Failed to save feed', { error: error.message });
      throw error;
    }
  }

  /**
   * Update feed with new episode
   */
  async updateFeed(podcastId, language, newEpisode) {
    try {
      logger.info('Updating RSS feed with new episode', { podcastId, language });

      // Get existing episodes
      const episodes = await this.getEpisodes(podcastId, language);

      // Add new episode
      episodes.unshift(newEpisode);

      // Regenerate feed
      await this.generateFeed(podcastId, language, episodes);

      return `${this.baseUrl}/${podcastId}/${language}`;

    } catch (error) {
      logger.error('Failed to update RSS feed', { error: error.message });
      throw error;
    }
  }

  /**
   * Generate podcast sitemap
   */
  async generateSitemap(podcastId) {
    try {
      logger.info('Generating podcast sitemap', { podcastId });

      const languages = await this.getAvailableLanguages(podcastId);

      const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${languages.map(lang => `  <url>
    <loc>${this.baseUrl}/${podcastId}/${lang}</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>`).join('\n')}
</urlset>`;

      const sitemapPath = path.join(this.feedsDir, podcastId, 'sitemap.xml');
      await fs.writeFile(sitemapPath, sitemap, 'utf-8');

      logger.info('Sitemap generated', { sitemapPath });

      return sitemapPath;

    } catch (error) {
      logger.error('Failed to generate sitemap', { error: error.message });
      throw error;
    }
  }

  /**
   * Helper: Format duration from seconds to iTunes format
   */
  formatDuration(seconds) {
    if (!seconds) return '00:00:00';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return [
      hours.toString().padStart(2, '0'),
      minutes.toString().padStart(2, '0'),
      secs.toString().padStart(2, '0')
    ].join(':');
  }

  /**
   * Helper: Get podcast data (placeholder - would fetch from database)
   */
  async getPodcastData(podcastId, language) {
    // In production, this would fetch from database
    return {
      title: 'My Podcast',
      description: 'A great podcast about technology',
      author: 'John Doe',
      email: 'john@example.com',
      websiteUrl: 'https://example.com',
      coverImageUrl: 'https://example.com/cover.jpg',
      category: 'Technology',
      explicit: false
    };
  }

  /**
   * Helper: Get episodes (placeholder - would fetch from database)
   */
  async getEpisodes(podcastId, language) {
    // In production, this would fetch from database
    return [];
  }

  /**
   * Helper: Get available languages (placeholder)
   */
  async getAvailableLanguages(podcastId) {
    // In production, this would fetch from database
    return ['en', 'es', 'fr', 'de'];
  }
}

module.exports = RSSService;
