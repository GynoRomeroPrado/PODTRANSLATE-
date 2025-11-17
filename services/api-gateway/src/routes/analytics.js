const express = require('express');
const router = express.Router();

// Analytics routes
router.get('/podcasts/:id', (req, res) => {
  res.status(501).json({ message: 'Not implemented yet' });
});

router.get('/episodes/:id', (req, res) => {
  res.status(501).json({ message: 'Not implemented yet' });
});

module.exports = router;
