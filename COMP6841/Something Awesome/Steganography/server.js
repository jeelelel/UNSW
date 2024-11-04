const express = require('express');
const path = require('path');
const multer = require('multer');
const { spawn } = require('child_process');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;


app.use(express.json());
app.use(express.urlencoded({ extended: true }));


const upload = multer({
  dest: 'uploads/',
  //limits: { fileSize: 100 * 1024 * 1024 }  // Limit file size to 100 MB
});

// Middleware to parse JSON and url-encoded data
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Route for the home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Serve static files from 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Route for encoding a photo
app.post('/encode-photo', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = req.file.path;
  const secretKey = req.body.secretKey || "default_secret";

  const pythonProcess = spawn('python3', ['public/photo_steganography.py', 'encode', filePath, secretKey]);

  pythonProcess.stdout.on('data', (data) => {
    const encodedImagePath = data.toString().trim();
    if (fs.existsSync(encodedImagePath)) {
      res.download(encodedImagePath, (err) => {
        if (err) {
          console.error(`Error downloading file: ${err}`);
          res.status(500).json({ error: 'Error downloading encoded image' });
        }
        // Delete the file after sending
        fs.unlink(encodedImagePath, (unlinkErr) => {
          if (unlinkErr) console.error(`Error deleting file: ${unlinkErr}`);
        });
      });
    } else {
      res.status(500).json({ error: 'Encoded image not found.' });
    }
  });

  pythonProcess.stderr.on('data', (error) => {
    console.error(`Error: ${error}`);
    res.status(500).json({ error: 'Error running Python script' });
  });
});

// Route for encoding a random photo
app.post('/encode-random-photo', (req, res) => {
  const secretKey = req.body.secretKey || "default_secret";  // Get secret key from request body

  // Call Python script to get a random image and encode it with the secret key
  const pythonProcess = spawn('python3', ['public/photo_steganography.py', 'random', 'dummy_path', secretKey]);

  let encodedImagePath = '';

  // Capture stdout from Python script (this is where the encoded image path will be)
  pythonProcess.stdout.on('data', (data) => {
    encodedImagePath = data.toString().trim();  // Get the path of the encoded image
    console.log(`Python stdout: ${encodedImagePath}`);
  });

  // Capture any errors from Python script
  pythonProcess.stderr.on('data', (error) => {
    console.error(`Python stderr: ${error}`);
    res.status(500).json({ error: 'Error running Python script' });
  });

  // When the Python process finishes
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    if (code === 0 && fs.existsSync(encodedImagePath)) {
      // Ensure file exists before sending it
      res.download(encodedImagePath, 'encoded_random_photo.png', (err) => {
        if (err) {
          console.error(`Error downloading file: ${err}`);
          res.status(500).json({ error: 'Error downloading encoded image' });
        }
        // Optionally delete the file after sending it
        fs.unlink(encodedImagePath, (unlinkErr) => {
          if (unlinkErr) console.error(`Error deleting file: ${unlinkErr}`);
        });
      });
    } else {
      res.status(500).json({ error: 'Encoded image not found or process failed.' });
    }
  });

  pythonProcess.on('error', (err) => {
    console.error('Failed to start subprocess:', err);
    res.status(500).json({ error: 'Failed to start subprocess' });
  });
});


// Serve static files from 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Route for decoding a photo
app.post('/decode-photo', upload.single('file'), (req, res) => {
    const filePath = req.file.path; // Path of uploaded file

    // Call Python script to decode the image
    const pythonProcess = spawn('python3', ['public/photo_steganography.py', 'decode', filePath]);

    pythonProcess.stdout.on('data', (data) => {
        const decodedMessage = data.toString().trim(); // Get the decoded message from Python script
        res.json({ message: decodedMessage });
    });

    pythonProcess.stderr.on('data', (error) => {
        console.error(`Error: ${error}`);
        res.status(500).json({ error: 'Error running Python script' });
    });
});

app.post('/encode-audio', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  const filePath = req.file.path;
  const secretKey = req.body.secretKey || "default_secret";

  const pythonProcess = spawn('python3', ['public/audio_steganography.py', 'encode', filePath, secretKey]);

  let output = '';
  let errorOutput = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Error running Python script', details: errorOutput });
    }

    const encodedAudioPath = output.trim();
    if (fs.existsSync(encodedAudioPath)) {
      return res.json({ success: true, filePath: encodedAudioPath });
    } else {
      return res.status(500).json({ error: 'Encoded audio not found.' });
    }
  });
});

app.post('/decode-audio', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  const filePath = req.file.path;

  const pythonProcess = spawn('python3', ['public/audio_steganography.py', 'decode', filePath]);

  let output = '';
  let errorOutput = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Error running Python script', details: errorOutput });
    }

    const decodedMessage = output.trim();
    return res.json({ message: decodedMessage });
  });
});

// Route for generating a random melody-like audio file
app.post('/generate-random-audio', (req, res) => {
  // Call Python script to generate a random melody-like audio file
  const pythonProcess = spawn('python3', ['public/audio_steganography.py', 'generate_random_audio']);

  pythonProcess.stdout.on('data', (data) => {
    const generatedAudioPath = data.toString().trim(); // Get the path of the generated random melody-like .wav file
    
    // Check if the file exists before sending it for download
    if (fs.existsSync(generatedAudioPath)) {
      res.download(generatedAudioPath); // Automatically trigger download of generated random melody-like .wav file
    } else {
      res.status(500).json({ error: 'Generated random audio not found.' });
    }
  });

  pythonProcess.stderr.on('data', (error) => {
    console.error(`Error: ${error}`);
    res.status(500).json({ error: 'Error running Python script' });
  });
});

app.post('/encode-video', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

  console.log("Received encode video request");  // Log when request is received

  const filePath = req.file.path;
  const secretKey = req.body.secretKey || "default_secret";

  // Call Python script to encode video
  const pythonProcess = spawn('python3', ['public/video_steganography.py', 'encode', filePath, secretKey]);

  let output = '';
  let errorOutput = '';

  pythonProcess.stdout.on('data', (data) => {
      output += data.toString();  // Capture output from Python script (encoded file path)
      console.log(`Python stdout: ${output}`);  // Log Python stdout for debugging
  });

  pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();  // Capture errors from Python script
      console.error(`Python stderr: ${errorOutput}`);  // Log Python stderr for debugging
  });

  pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);  // Log process exit code

      if (code !== 0) {
          return res.status(500).json({ error: 'Error running Python script', details: errorOutput });
      }

      const encodedVideoPath = output.trim();  // Path to encoded video

      if (fs.existsSync(encodedVideoPath)) {
          res.download(encodedVideoPath, 'encoded_video.mp4', (err) => {
              if (err) {
                  console.error(`Error downloading file: ${err}`);
                  return res.status(500).json({ error: 'Error downloading encoded video' });
              }
              fs.unlink(encodedVideoPath, (unlinkErr) => {  // Optionally delete after sending
                  if (unlinkErr) console.error(`Error deleting file: ${unlinkErr}`);
              });
          });
      } else {
          return res.status(500).json({ error: 'Encoded video not found.' });
      }
  });
});

// Route for decoding a video
app.post('/decode-video', upload.single('file'), (req, res) => {
  console.log("Received decode video request");
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

  const filePath = req.file.path;

  // Call Python script to decode video
  const pythonProcess = spawn('python3', ['public/video_steganography.py', 'decode', filePath]);

  let output = '';
  let errorOutput = '';

  pythonProcess.stdout.on('data', (data) => {
      output += data.toString();  // Capture decoded message from Python script
  });

  pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();  // Capture errors from Python script
  });

  pythonProcess.on('close', (code) => {
      if (code !== 0) {
          return res.status(500).json({ error: 'Error running Python script', details: errorOutput });
      }

      const decodedMessage = output.trim();  // Decoded message

      return res.json({ message: decodedMessage });  // Send back decoded message as JSON
  });
});


// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});