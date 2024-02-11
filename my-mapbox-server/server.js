// Import necessary modules
const express = require('express');
const cors = require('cors');
const AWS = require('aws-sdk');
require('dotenv').config();

// Initialize express application
const app = express();

// Use CORS middleware to allow cross-origin requests
app.use(cors());

// Configure AWS with your credentials
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION,
});

// Create an S3 instance
const s3 = new AWS.S3();

// Define a route for generating pre-signed URLs
app.get('s3://tidalwaves/geojson', (req, res) => {
  const params = {
    Bucket: process.env.S3_BUCKET_NAME,
    Key: req.query.key, // Expect 'key' parameter to specify the S3 object key
    Expires: 60 * 5, // Link expires in 5 minutes
  };

  s3.getSignedUrl('getObject', params, (err, url) => {
    if (err) {
      console.error("Error generating pre-signed URL", err);
      return res.status(500).send("Error generating pre-signed URL");
    }
    res.json({ url });
  });
});

// Start the server
const port = 3000;
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});