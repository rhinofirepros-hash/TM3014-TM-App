#!/bin/bash

# T&M Daily Tag App - Quick Deploy Script
# This script prepares the app for deployment

echo "🚀 Preparing T&M Daily Tag App for Deployment..."

# Navigate to frontend directory
cd frontend

# Install dependencies if needed
echo "📦 Installing dependencies..."
yarn install

# Build the production version
echo "🔨 Building production version..."
yarn build

# Create a simple server.js for hosting (optional)
cat > server.js << 'EOF'
const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

// Serve static files from the React app build directory
app.use(express.static(path.join(__dirname, 'build')));

// Catch all handler: send back React's index.html file
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(port, () => {
  console.log(`T&M Tag App running on port ${port}`);
});
EOF

# Create package.json for production server
cat > package-server.json << 'EOF'
{
  "name": "tm-tag-app-server",
  "version": "1.0.0",
  "description": "T&M Daily Tag App Production Server",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "build": "echo 'Build completed'"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "engines": {
    "node": "16.x"
  }
}
EOF

echo "✅ Build completed!"
echo ""
echo "📋 Deployment Options:"
echo ""
echo "1. 🌐 Netlify (Recommended - Free):"
echo "   - Upload the 'build' folder to Netlify"
echo "   - Or connect your GitHub repo"
echo ""
echo "2. 🚀 Vercel (Easy Deploy):"
echo "   - Run: npm i -g vercel"
echo "   - Run: vercel --prod"
echo ""
echo "3. 📱 Heroku (Full Stack):"
echo "   - Copy package-server.json to package.json"
echo "   - Run: git add . && git commit -m 'Deploy'"
echo "   - Run: heroku create your-tm-app"
echo "   - Run: git push heroku main"
echo ""
echo "4. 💻 Self-Host:"
echo "   - Copy 'build' folder to your web server"
echo "   - Point domain to the build folder"
echo ""
echo "🎉 Your T&M Daily Tag App is ready for deployment!"
echo "📁 Built files are in: ./build/"
echo ""
echo "🔗 Quick Deploy Links:"
echo "   Netlify: https://app.netlify.com/drop"
echo "   Vercel:  https://vercel.com/new"
echo ""

# Go back to root
cd ..